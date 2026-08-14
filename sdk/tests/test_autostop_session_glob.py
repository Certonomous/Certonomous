"""The auto-stop control-room clause must not name ONE session directory.

WHY THIS FILE EXISTS (D65, 2026-08-14)
--------------------------------------
`scripts/auto-stop.sh` clause (3) holds the box while a Claude session
transcript is being written -- that is what stops the machine powering off
under an occupied control room, the 2026-07-30 and 2026-08-12 failures. It
shipped on 2026-08-12 naming one directory:

    SESSIONS=${SESSIONS:-/home/ubuntu/.claude-sanaa/projects/-home-ubuntu-Certonomous}

The session config directory was migrated afterwards. Measured at 22:04Z on
2026-08-14, the live transcript under `/home/ubuntu/.claude/projects/...` was
advancing every few seconds while the named directory had not been written
since 21:46:43Z -- so the clause was firing off a quiescent copy, by accident,
and was ~12 minutes from going silent with five agents at work.

THE DEFECT CLASS, WHICH IS THE PART WORTH KEEPING: the test was not wrong. Its
REFERENT moved. A check that names its subject by a path inherits every
migration of that path, and this one fails silently, because a directory that
stopped receiving writes is indistinguishable from a directory nobody is
working in. Same shape as D48 (a guard reading a pinned board after the world
moved) and D55. Re-typing the new path would rebuild the defect one migration
later, so the clause scans a GLOB and this file refuses a return to a constant.

WHAT IS ASSERTED, AND WHY EACH ASSERTION IS HERE
------------------------------------------------
* The default `SESSIONS` CONTAINS A GLOB METACHARACTER. This is the assertion
  that reddens if someone hardcodes one directory again, and it is deliberately
  independent of which directories happen to exist on the host running it --
  on a box where only one config dir exists, a coverage test alone would pass a
  hardcoded path.
* The default COVERS every config directory this host actually has, discovered
  from the repo path rather than from the script's own constant, so the two
  sides cannot agree by being the same string.
* A fresh transcript in EITHER directory holds the box -- run both ways round,
  because a clause that only ever reads the first match is the same bug wearing
  a glob.
* THE NEGATIVE PATH FIRES. Stale transcripts everywhere and the box still
  stops. A fix that makes the box never power off has replaced a cost control
  with a bill, which is worse than the defect it repaired (L-84: a positive
  control proves an instrument can fire, never that it fires only where it
  should).
* A GLOB THAT MATCHES NOTHING IS LOUD AND IS NOT A HOLD. Silently evaluating to
  false is how an empty room and a blind instrument became the same reading;
  holding the box forever whenever it is misconfigured is the bill again.
* The overrides these controls steer with are shown to actually steer, because
  a fixture the script ignored would make every case above pass for the wrong
  reason.

HOW THESE RUN, AND THE TRAP THEY AVOID
--------------------------------------
Each case executes the REAL `scripts/auto-stop.sh` under `DRY_RUN=1` with a
scrubbed environment. Scrubbed is not tidiness: this lab's interactive shells
replace `find` with `bfs`, and `bfs` REJECTS `-newermt "-30 min"` as an invalid
timestamp. Inheriting an exported shell function here would measure a `find`
that root's cron never runs, which is exactly the false finding this file would
then certify. Root cron runs GNU find on a plain PATH, so that is what is used.
"""

from __future__ import annotations

import glob as globmodule
import os
import re
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "auto-stop.sh"

#: The PATH root cron actually runs the gate with. Never the caller's.
CRON_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

#: `SESSIONS=${SESSIONS:-<default>}` -- the constant under test.
_SESSIONS_DEFAULT = re.compile(r"^SESSIONS=\$\{SESSIONS:-(.*)\}\s*$", re.M)

GLOB_METACHARACTERS = "*?["


def default_sessions() -> str:
    text = SCRIPT.read_text()
    match = _SESSIONS_DEFAULT.search(text)
    if match is None:
        raise AssertionError(
            f"no `SESSIONS=${{SESSIONS:-...}}` assignment found in {SCRIPT}. "
            "Either the control-room clause lost its override -- which would "
            "make the negative path untestable, the way the pre-2026-08-12 "
            "gate was -- or it was spelled some way this check cannot read, "
            "which is the same problem for the next reader.")
    return match.group(1)


def config_dirs_on_this_host() -> list[Path]:
    """Session directories for THIS repo, discovered from the repo path.

    Deliberately NOT read from the script's own constant: a coverage check that
    asks the script where to look and then confirms it looked there is a
    tautology. The slug is how the config directory names a project -- the
    absolute path with separators replaced -- so this derivation follows the
    repo, not the gate.
    """
    slug = str(REPO).replace("/", "-")
    found = []
    for root in sorted(Path.home().glob(".claude*")):
        candidate = root / "projects" / slug
        if candidate.is_dir():
            found.append(candidate)
    return found


def run_gate(sessions: str, marker_age_min: int, repo: Path,
             idle_minutes: int = 30) -> str:
    """Execute the real gate, dry, and return everything it said."""
    marker = repo / "marker"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("")
    old = time.time() - marker_age_min * 60
    os.utime(marker, (old, old))
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        env={"PATH": CRON_PATH, "DRY_RUN": "1",
             "IDLE_MINUTES": str(idle_minutes), "MARKER": str(marker),
             # A repo path with no `.autostop-hold` under it, so clause (0)
             # cannot short-circuit the case and quietly pass everything.
             "REPO": str(repo / "no-such-repo"),
             "SESSIONS": sessions},
        capture_output=True, text=True, timeout=120)
    return result.stdout + result.stderr


def plant(root: Path, config_dir_name: str, age_min: float) -> Path:
    """A transcript of a given age in a named scratch config directory."""
    d = root / config_dir_name / "projects" / str(REPO).replace("/", "-")
    d.mkdir(parents=True, exist_ok=True)
    f = d / "session.jsonl"
    f.write_text('{"type":"user"}\n')
    when = time.time() - age_min * 60
    os.utime(f, (when, when))
    return f


def scratch_pattern(root: Path) -> str:
    return str(root / ".claude*" / "projects" / str(REPO).replace("/", "-"))


class TheDefaultMustNotNameOneDirectoryTests(unittest.TestCase):
    """The anti-hardcode invariant. This is what reddens on a relapse."""

    def test_the_default_sessions_is_a_pattern_and_not_a_single_path(self):
        default = default_sessions()
        self.assertTrue(
            any(c in default for c in GLOB_METACHARACTERS),
            "scripts/auto-stop.sh clause (3) is back to naming ONE session "
            f"directory: SESSIONS defaults to {default!r}. That is the D65 "
            "defect verbatim -- on 2026-08-14 the named directory stopped "
            "being where the live session writes, the clause went on reading "
            "a quiescent copy, and an occupied control room was about to read "
            "as an empty one. A path is a referent that migrates; the clause "
            "must scan every config directory, e.g. "
            "/home/ubuntu/.claude*/projects/<repo-slug>.")

    def test_the_default_covers_every_config_directory_on_this_host(self):
        """Reach, measured against a set derived independently of the gate."""
        present = config_dirs_on_this_host()
        if not present:
            self.skipTest(
                "this host has no session config directory for this repo, so "
                "there is nothing for the gate to cover here. Stated rather "
                "than passed silently: on such a host this test proves "
                "nothing and test_the_default_sessions_is_a_pattern... is the "
                "only thing standing between the gate and a hardcoded path")
        covered = set()
        for pattern in default_sessions().split():
            covered.update(Path(p).resolve()
                           for p in globmodule.glob(pattern))
        print(f"\n[autostop-sessions] config dirs on this host: "
              f"{', '.join(str(p) for p in present)}")
        missed = [p for p in present if p.resolve() not in covered]
        self.assertEqual(
            [], missed,
            "session config director(ies) exist for this repo that the "
            "auto-stop control-room clause does not scan, so a session "
            "writing there would not hold the box: "
            + ", ".join(str(p) for p in missed))


class TheClauseIsShownToFireBothWaysTests(unittest.TestCase):
    """Planted fixtures, run through the real script.

    Both directions and the empty case, because the failure being repaired is
    not "the clause never fires" -- it fired the whole time, off the wrong
    directory.
    """

    def test_a_fresh_transcript_in_the_migrated_directory_holds_the_box(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plant(root, ".claude", age_min=0)          # where the live one is
            plant(root, ".claude-sanaa", age_min=90)   # the copy left behind
            out = run_gate(scratch_pattern(root), marker_age_min=90, repo=root)
        self.assertIn("ALIVE", out, out)
        self.assertIn(
            ".claude/projects", out,
            "the box was held, but not by the directory that is actually "
            "being written to -- which is the D65 accident, not the repair:\n"
            + out)

    def test_a_fresh_transcript_in_the_older_directory_also_holds_the_box(self):
        """The other order. A glob read only up to its first hit is the bug."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plant(root, ".claude", age_min=90)
            plant(root, ".claude-sanaa", age_min=0)
            out = run_gate(scratch_pattern(root), marker_age_min=90, repo=root)
        self.assertIn("ALIVE", out, out)
        self.assertIn(".claude-sanaa/projects", out, out)

    def test_a_genuinely_idle_box_still_powers_itself_off(self):
        """THE NEGATIVE PATH. Without this the fix could be `keep` always.

        A gate that never stops the box is not a repaired cost control, it is
        a bill, and it would be a worse defect than the one D65 records.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plant(root, ".claude", age_min=90)
            plant(root, ".claude-sanaa", age_min=90)
            out = run_gate(scratch_pattern(root), marker_age_min=90, repo=root)
        self.assertNotIn("ALIVE", out, "stale transcripts in every config "
                                       "directory held the box:\n" + out)
        self.assertIn("shutting down", out, out)

    def test_a_pattern_matching_nothing_is_announced_and_does_not_hold(self):
        """Neither a silent false nor a silent hold.

        A silent false is how a blind instrument and an empty control room
        became the same reading. A hold is how a misconfigured gate becomes a
        machine nobody can switch off.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = run_gate(scratch_pattern(root), marker_age_min=90, repo=root)
        self.assertIn("BLIND", out, "the control-room clause found no "
                                    "directory to scan and said nothing:\n"
                                    + out)
        self.assertNotIn("ALIVE", out, "a pattern matching nothing pinned the "
                                       "box awake:\n" + out)
        self.assertIn("shutting down", out, out)


class TheHarnessIsShownToSteerTests(unittest.TestCase):
    """The door every control above uses, asserted directly (L-84).

    If `SESSIONS` did not actually reach the clause, every planted case would
    be reading the REAL directories and passing for a reason nobody intended.
    """

    def test_the_sessions_override_is_what_decides_the_planted_cases(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plant(root, ".claude", age_min=0)
            held = run_gate(scratch_pattern(root), marker_age_min=90, repo=root)
            # Same fixture, same instant, pointed somewhere empty.
            missed = run_gate(str(root / "nowhere*" / "projects" / "x"),
                              marker_age_min=90, repo=root)
        self.assertIn("ALIVE", held, held)
        self.assertNotIn(
            "ALIVE", missed,
            "the gate held the box while SESSIONS pointed at nothing, so the "
            "planted transcripts are not what these controls are measuring:\n"
            + missed)

    def test_the_gate_under_test_is_the_tracked_file(self):
        self.assertTrue(SCRIPT.is_file(), f"{SCRIPT} is missing")
        self.assertIn("clause (3)", SCRIPT.read_text(),
                      "the control-room clause is not where this file thinks "
                      "it is; these controls may be exercising nothing")


if __name__ == "__main__":
    unittest.main()
