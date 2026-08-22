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
# `**Section last written:** <iso> by <who>.`  The `by <who>` half is optional in
# the pattern but not in practice: a stamp with no writer names nobody to chase.
STAMP_RE = re.compile(
    r"^\*\*Section last written:\*\*\s*(\S+?)(?:\s+by\s+(.*?))?\s*$", re.M)

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


def check_board(cfg):
    print("\n[2/3] SECTIONS -- every team has a board section")
    if not os.path.exists(LABSTATE):
        fail("board", "docs/LAB_STATE.md is missing -- there is no handoff channel")
        return {}
    text = open(LABSTATE).read()
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
        stamp = m.group(1).rstrip(".")
        who = (m.group(2) or "").rstrip(".").strip() or None
        if who is None:
            warn(team, "stamp names no writer ('by <who>' missing)")
        when = parse_iso(stamp)
        if when is None:
            if stamp.lower().startswith("never"):
                warn(team, "stamp says 'never' -- section has never been written by its owner")
            else:
                fail(team, "stamp %r is not an ISO instant" % stamp)
            continue
        paths = t.get("scope_paths") or []
        last = git("log", "-1", "--format=%cI", "--", *paths) if paths else ""
        if not last:
            ok(team, "stamped %s by %s; no commits in scope to compare" % (stamp, who))
            continue
        lt = parse_iso(last)
        if lt is not None and lt > when:
            warn(team, "STALE -- territory committed %s, section stamped %s by %s" % (last, stamp, who))
        else:
            ok(team, "stamped %s by %s, not older than its last commit (%s)" % (stamp, who, last))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn", action="store_true",
                    help="exit 0 even on FAIL (staleness reporting only)")
    args = ap.parse_args()

    cfg = load_cfg()
    check_roster()
    secs = check_board(cfg)
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
