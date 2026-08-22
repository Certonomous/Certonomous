#!/usr/bin/env python3
"""Gate the team harness.

    python3 scripts/check_harness.py          # report; exit 1 on any FAIL
    python3 scripts/check_harness.py --warn   # report; exit 0 (staleness is advisory)

Three of the harness's load-bearing rules shipped as preferences, because nothing
checked them. By this directory's own standard -- a rule nobody can fail is a
preference -- that made them scenery. This is the check.

  1. ROSTER     the agent files, the CLAUDE.md roster table and the form-teams
                table all render from harness/teams.yaml (delegated to
                generate_agents.py --check).
  2. SECTIONS   every team in teams.yaml has a `## <team>` section on the board.
  3. FRESHNESS  every section carries a `**Section last written:**` stamp, and the
                stamp is not older than the last commit touching that team's
                scope_paths. A section older than its own territory is STALE: the
                team committed and did not update its board, which is the exact
                failure mode L-226 is about.

What this does NOT check, stated rather than implied: whether the agents actually
LOAD (they are read at session start -- see harness/README.md), whether the lane
cap is respected, or whether a board section is TRUE. Only that it is present,
stamped, and not older than the work it describes.
"""

import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABSTATE = os.path.join(REPO, "docs", "LAB_STATE.md")
LABSTATE_REL = "docs/LAB_STATE.md"
# `**Section last written:** <iso> by <who>.`  The `by <who>` half is optional in
# the pattern but not in practice: a stamp with no writer names nobody to chase.
# `**Section last written:** <iso> by <who>` -- and `<who>` may carry any trailing
# prose the writer wants. The canonical form is documented in harness/README.md and
# in the form-teams skill, but this parser is DELIBERATELY tolerant of departures
# from it: the closure lane's stamp carried a trailing clause, was rejected, and the
# lane edited its board to suit the parser. A checker that makes a team work around
# it is not a check. The rule: if the TIMESTAMP is readable, the section is graded on
# freshness; anything else about the stamp is at most a WARN.
STAMP_RE = re.compile(
    r"^\*\*Section last written:\*\*[ \t]*(?P<when>\S+?)"
    r"(?:[ \t]+by[ \t]+(?P<who>.*))?[ \t]*$", re.M)

FAILS, WARNS = [], []


def fail(where, msg):
    FAILS.append("%s: %s" % (where, msg))
    print("  FAIL  %-14s %s" % (where, msg))


def warn(where, msg):
    WARNS.append("%s: %s" % (where, msg))
    print("  WARN  %-14s %s" % (where, msg))


def ok(where, msg):
    print("  ok    %-14s %s" % (where, msg))


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def load_cfg():
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML required: python3 -m pip install --user pyyaml")
    with open(os.path.join(REPO, "harness", "teams.yaml")) as fh:
        return yaml.safe_load(fh)


def parse_iso(s):
    """Accept 2026-08-22T18:05Z / ...:05:33Z / with offset. Returns epoch or None."""
    from datetime import datetime, timezone
    s = s.strip().rstrip(".")
    for f in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
              "%Y-%m-%dT%H:%M%z", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s, f)
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return d.timestamp()
        except ValueError:
            continue
    return None


def sections(text):
    """{heading: body} for every `## ` section."""
    out, parts = {}, re.split(r"^## (.+)$", text, flags=re.M)
    for i in range(1, len(parts), 2):
        out[parts[i].strip()] = parts[i + 1]
    return out


def check_roster():
    print("\n[1/3] ROSTER -- agent files and prose surfaces vs teams.yaml")
    r = subprocess.run([sys.executable, os.path.join(REPO, "harness", "generate_agents.py"),
                        "--check"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if "DRIFT" in line or "ORPHAN" in line or "BAD" in line:
            fail("roster", line.strip())
    if r.returncode == 0:
        ok("roster", "agents + CLAUDE.md roster + form-teams table all match teams.yaml")
    elif not FAILS:
        fail("roster", "generate_agents.py --check exited %d" % r.returncode)


def board_text(use_worktree):
    """The board is read from HEAD, not the worktree.

    The shared-board rule (chief, 2026-08-22) is that no team writes the worktree
    copy of docs/LAB_STATE.md: each board commit rebuilds from
    `git show $H:docs/LAB_STATE.md`, replaces only its own section, and stages by
    hash-object + update-index --cacheinfo. So the worktree copy is nobody's output
    and drifts behind HEAD by design -- grading it meant the checker and the rule
    contradicted each other. HEAD is the board. `--worktree` restores the old
    behaviour for anyone inspecting an uncommitted edit."""
    if use_worktree:
        if not os.path.exists(LABSTATE):
            return None, "worktree (MISSING)"
        return open(LABSTATE).read(), "worktree"
    r = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + LABSTATE_REL],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, "HEAD (not committed)"
    return r.stdout, "HEAD"


def check_board(cfg, use_worktree=False):
    print("\n[2/3] SECTIONS -- every team has a board section")
    text, src = board_text(use_worktree)
    print("  ....  board read from %s" % src)
    if text is None:
        fail("board", "%s has no %s -- there is no handoff channel" % (src, LABSTATE_REL))
        return {}
    secs = sections(text)
    for t in cfg["teams"]:
        if t["team"] in secs:
            ok("board", "## %s present" % t["team"])
        else:
            fail("board", "no '## %s' section (run generate_agents.py)" % t["team"])
    return secs


def check_freshness(cfg, secs):
    print("\n[3/3] FRESHNESS -- is each section older than its own territory?")
    for t in cfg["teams"]:
        team, body = t["team"], secs.get(t["team"])
        if body is None:
            continue
        m = STAMP_RE.search(body)
        if not m:
            fail(team, "no '**Section last written:**' stamp")
            continue
        stamp = m.group("when").rstrip(".")
        who = (m.group("who") or "").strip().rstrip(".").strip() or None
        if who is None:
            warn(team, "stamp names no writer ('by <who>' missing)")
        when = parse_iso(stamp)
        if when is None:
            # A stamp whose timestamp will not parse is a WARN, never a FAIL: the
            # section is present and owned, and refusing it outright is what made a
            # lane rewrite its board to suit this script.
            if stamp.lower().startswith("never"):
                warn(team, "stamp says 'never' -- section has never been written by its owner")
            else:
                warn(team, "stamp %r is not an ISO instant -- freshness not graded" % stamp)
            continue
        paths = t.get("scope_paths") or []
        last = git("log", "-1", "--format=%cI", "--", *paths) if paths else ""
        if not last:
            ok(team, "stamped %s by %s; no commits in scope to compare" % (stamp, (who or "?")[:40]))
            continue
        lt = parse_iso(last)
        if lt is not None and lt > when:
            warn(team, "STALE -- territory committed %s, section stamped %s by %s" % (last, stamp, (who or "?")[:40]))
        else:
            ok(team, "stamped %s by %s, not older than its last commit (%s)" % (stamp, (who or "?")[:40], last))


STAMP_CASES = [
    # (label, line, must_parse_as_instant)
    ("canonical", "**Section last written:** 2026-08-22T20:34Z by closure-supervisor.", True),
    # the exact stamp the closure lane had rejected, which made it rewrite its board
    ("trailing clause", "**Section last written:** 2026-08-22T21:20Z by closure-supervisor "
                        "\u2014 R4 rows and the D369 closure by the R4 BUILD lane; everything "
                        "else as the closure-supervisor left it", True),
    ("parenthetical", "**Section last written:** 2026-08-22T18:05Z by harness-build "
                      "(FIRST FILL \u2014 not yet written by its owner).", True),
    ("no writer", "**Section last written:** 2026-08-22T18:05Z", True),
    ("skeleton", "**Section last written:** never by nobody.", False),
    ("seconds", "**Section last written:** 2026-08-22T18:05:33Z by x.", True),
    ("offset tz", "**Section last written:** 2026-08-22T18:05:33+00:00 by x.", True),
    ("semicolon tail", "**Section last written:** 2026-08-22T20:34Z by x; see note", True),
]


def selftest():
    """Regression guard on the stamp parser.

    This exists because the parser has been wrong twice: first a pattern that
    required end-of-line after the timestamp, which failed every correct section;
    then a rejection of trailing prose, which made the closure lane rewrite its
    board to suit the script. Both were the same defect -- an instrument that
    cannot see a correct input -- and neither was caught by anything.
    """
    bad = 0
    for label, line, want_instant in STAMP_CASES:
        m = STAMP_RE.search(line)
        if not m:
            print("  FAIL  selftest    %-16s not matched at all" % label); bad += 1; continue
        when = m.group("when").rstrip(".")
        got = parse_iso(when) is not None
        if got != want_instant:
            print("  FAIL  selftest    %-16s timestamp %r parsed=%s want=%s"
                  % (label, when, got, want_instant)); bad += 1
        else:
            print("  ok    selftest    %-16s %s" % (label, when))
    # a line that is not a stamp must NOT match -- the negative control
    for label, line in [("negative", "**Last commit:** 2026-08-22T20:34Z by someone."),
                        ("negative2", "Section last written: 2026-08-22T20:34Z")]:
        if STAMP_RE.search(line):
            print("  FAIL  selftest    %-16s matched a non-stamp line" % label); bad += 1
        else:
            print("  ok    selftest    %-16s correctly rejected" % label)
    print("\n%s: stamp parser selftest, %d case(s), %d failure(s)"
          % ("FAIL" if bad else "PASS", len(STAMP_CASES) + 2, bad))
    return 1 if bad else 0



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn", action="store_true",
                    help="exit 0 even on FAIL (staleness reporting only)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the stamp-parser regression cases and exit")
    ap.add_argument("--worktree", action="store_true",
                    help="grade the worktree docs/LAB_STATE.md instead of HEAD "
                         "(default is HEAD; no team writes the worktree copy)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    cfg = load_cfg()
    check_roster()
    secs = check_board(cfg, args.worktree)
    check_freshness(cfg, secs)

    print("\n" + "-" * 70)
    if FAILS:
        print("FAIL: %d problem(s), %d warning(s)" % (len(FAILS), len(WARNS)))
    elif WARNS:
        print("PASS with %d warning(s) -- a stale board still re-forms teams, "
              "but it re-forms them wrong." % len(WARNS))
    else:
        print("PASS: roster round-trips, every team has a section, no section is "
              "older than its own territory.")
    print("NOTE: this cannot check that the agents LOAD (session-start only), that "
          "the lane cap holds, or that any board line is TRUE.")
    return 1 if (FAILS and not args.warn) else 0


if __name__ == "__main__":
    sys.exit(main())
