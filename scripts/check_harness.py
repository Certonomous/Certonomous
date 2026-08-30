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
  3. FRESHNESS  a section is stale when its team committed work and did not update
                its board -- the failure L-226 is about. Graded COMMIT TO COMMIT:
                the commit that last changed the section versus the latest commit
                touching the team's scope_paths, both machine timestamps. The
                hand-written stamp is a 10-minute-tolerance FALLBACK used only when
                the section's own commit cannot be determined, because the stamp is
                typed at minute resolution just before `commit-tree` and produced
                false STALE for every team that did the right thing.
  4. PROVENANCE a block RECORDED as landed is still present in its file
                BYTE-FOR-BYTE. This is the DETECTION half of the unquoted-heredoc
                defect (L-403/L-405): append_block.py protects the writes that go
                THROUGH it, and nothing asked the same question afterwards. Its
                population is the ledger it reads, so an empty ledger is reported
                NOT MEASURED and never ok.

What this does NOT check, stated rather than implied: whether the agents actually
LOAD (they are read at session start -- see harness/README.md), whether the lane
cap is respected, or whether a board section is TRUE. Only that it is present,
stamped, and not older than the work it describes.

It also does NOT treat overlapping scope_paths between teams as a conflict, and
never has: scope_paths are the freshness gate's territory query, not an
ownership claim. Two teams may legitimately watch one path (the verification
team keeps docs/papers/verification_validation/; the ansys-verification team
names the Ansys manual and its sidecar inside it by explicit path, 2026-08-24).
"""

import argparse
import base64
import hashlib
import json
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
    print("\n[1/5] ROSTER -- agent files and prose surfaces vs teams.yaml")
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
    print("\n[2/5] SECTIONS -- every team has a board section")
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


STAMP_TOLERANCE_S = 600   # 10 minutes -- see freshness_verdict()

_BOARD_CACHE = {}


def board_at(sha):
    if sha not in _BOARD_CACHE:
        _BOARD_CACHE[sha] = git("show", "%s:%s" % (sha, LABSTATE_REL))
    return _BOARD_CACHE[sha]


def section_commit(team, limit=40):
    """The newest commit that actually CHANGED this team's section of the board.

    Walks the commits that touched docs/LAB_STATE.md, newest first, and compares
    each one's rendering of `## <team>` against the next-older one. The first
    difference is the commit that last wrote the section. Returns (sha, epoch), or
    (None, None) if the section never changed inside the window -- in which case
    the caller falls back to the hand-written stamp.
    """
    log = git("log", "--format=%H %cI", "-n", str(limit), "--", LABSTATE_REL)
    rows = [l.split(None, 1) for l in log.splitlines() if l.strip()]
    if not rows:
        return None, None
    bodies = [(sha, iso, sections(board_at(sha)).get(team)) for sha, iso in rows]
    for i, (sha, iso, body) in enumerate(bodies):
        older = bodies[i + 1][2] if i + 1 < len(bodies) else None
        if body != older:
            return sha, parse_iso(iso)
    return None, None


def freshness_verdict(territory_sha, territory_t, section_sha, section_t, stamp_t):
    """Is this section stale? Pure function, so --selftest can exercise it.

    PRIMARY is commit-to-commit: the commit that last changed the section versus
    the latest commit touching the team's territory. BOTH SIDES ARE MACHINE
    TIMESTAMPS, so this is exact.

    FALLBACK, only when the section's own commit cannot be determined, is the
    hand-written stamp with a 10-minute tolerance. That tolerance exists because
    the stamp is typed at MINUTE resolution moments before `commit-tree` runs: a
    section stamped 20:55Z landing at 20:56:27 was read as "older than its
    territory" and reported STALE, systematically, for every team that correctly
    updated its board in the same commit as its work. The bug was in the clock,
    not the board.

    Returns (status, reason) where status is "ok" or "stale".
    """
    if territory_sha is None or territory_t is None:
        return "ok", "no commits in its scope to compare against"

    if section_sha is not None and section_t is not None:
        if section_sha == territory_sha:
            return "ok", ("board and territory landed in the SAME commit %s"
                          % territory_sha[:8])
        if section_t >= territory_t:
            return "ok", ("section committed at %s, at or after territory %s"
                          % (iso_of(section_t), territory_sha[:8]))
        return "stale", ("territory committed %s at %s, section last changed %s at %s"
                         % (territory_sha[:8], iso_of(territory_t),
                            section_sha[:8], iso_of(section_t)))

    # fallback: no determinable section commit
    if stamp_t is None:
        return "ok", "no section commit and no parseable stamp -- freshness not graded"
    if stamp_t >= territory_t - STAMP_TOLERANCE_S:
        return "ok", ("stamp %s within %d min of territory commit %s (fallback)"
                      % (iso_of(stamp_t), STAMP_TOLERANCE_S // 60, territory_sha[:8]))
    return "stale", ("stamp %s is more than %d min before territory commit %s at %s"
                     % (iso_of(stamp_t), STAMP_TOLERANCE_S // 60,
                        territory_sha[:8], iso_of(territory_t)))


def iso_of(epoch):
    import datetime
    if epoch is None:
        return "?"
    return datetime.datetime.fromtimestamp(
        epoch, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_freshness(cfg, secs):
    print("\n[3/5] FRESHNESS -- is each section older than its own territory?")
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
        stamp_t = parse_iso(stamp)
        if stamp_t is None and stamp.lower().startswith("never"):
            warn(team, "stamp says 'never' -- section has never been written by its owner")
            continue

        paths = t.get("scope_paths") or []
        terr = git("log", "-1", "--format=%H %cI", "--", *paths) if paths else ""
        if terr:
            tsha, tiso = terr.split(None, 1)
            tt = parse_iso(tiso)
        else:
            tsha, tt = None, None
        ssha, st = section_commit(team)

        status, reason = freshness_verdict(tsha, tt, ssha, st, stamp_t)
        label = "stamped %s by %s" % (stamp, (who or "?")[:32])
        if status == "stale":
            warn(team, "STALE -- %s (%s)" % (reason, label))
        else:
            ok(team, "%s -- %s" % (reason, label))


# ---------------------------------------------------------------------------
# [4/5] PROVENANCE -- the DETECTION half of the unquoted-heredoc defect.
#
# append_block.py removed the heredoc from the WRITE path and proves, at the
# instant of the append, that the landed bytes are the source bytes. That
# guarantee then evaporates: nothing afterwards could ask whether the block that
# landed is still the block that landed, and nothing at all sees a block written
# by hand, by heredoc, or by an older path. This clause asks the later question,
# for every block that carries a record.
#
# THE HONESTY CONDITION. The clause is only as wide as the ledger, and on the day
# it landed the ledger held ZERO records -- every block in the tree predates the
# recorder. A clause that returns green over an empty population is the fail-open
# shape this team has now measured five times (queue_entry_check with no args
# returns 0; the reconciler's DEFAULT_PATHS; append_record.py's `if new_ids:`).
# So an empty population is NOT MEASURED, never ok, and --strict-provenance turns
# it into a FAIL for whoever wants the gate armed.
# ---------------------------------------------------------------------------

PROV_LEDGER_REL = "verification/credibility/append_block_provenance.jsonl"


def heredoc_shadow(b):
    """The bytes an UNQUOTED heredoc would have produced from these bytes.

    Command substitution replaces every `...` and $(...) span with the command's
    OUTPUT, which for the prose shapes at issue -- `GATE FAIL` eaten out of
    docs/LAB_STATE.md, `Queue:` eaten out of a charter -- is the empty string.
    Computing the shadow lets the clause name WHICH defect it is looking at
    rather than only reporting that the bytes changed.
    """
    b = re.sub(rb"`[^`\n]*`", b"", b)
    return re.sub(rb"\$\([^()\n]*\)", b"", b)


def load_provenance(path):
    """Returns a list of records, or None when the ledger does not exist.

    An unreadable line becomes a {"_bad": ...} record rather than an exception: a
    corrupt ledger is precisely the failure this clause exists to notice, so it
    must be reported, not raised over.
    """
    if not os.path.exists(path):
        return None
    recs = []
    with open(path, "rb") as fh:
        for n, raw in enumerate(fh, 1):
            if not raw.strip():
                continue
            try:
                r = json.loads(raw.decode("utf-8"))
                if not isinstance(r, dict):
                    raise ValueError("not a JSON object")
            except Exception as e:
                recs.append({"_bad": "ledger line %d is unreadable: %s" % (n, e)})
                continue
            r["_line"] = n
            recs.append(r)
    return recs


def provenance_verdict(records, read_bytes):
    """Pure function, so --selftest can exercise it. Returns [(status, label, msg)].

    read_bytes(target) -> bytes   grade this record against these file bytes
                       -> None    the target is gone   -> FAIL
                       -> False   the target is out of this repo -> not graded

    status is one of: ok / fail / superseded / skip.
    """
    out = []
    # SUPERSESSION. The shared-board protocol REWRITES a section wholesale (rebuild
    # from HEAD, replace only your own `## <team>`), so an earlier record for the
    # same heading makes no claim about today's file. Without this the clause would
    # flag every team that correctly updated its board -- the same defect this
    # file's own stamp parser shipped twice: an instrument that cannot see a
    # correct input.
    last = {}
    for i, r in enumerate(records):
        if "_bad" not in r:
            last[(r.get("target"), r.get("section") or r.get("sha256"))] = i

    for i, r in enumerate(records):
        if "_bad" in r:
            out.append(("fail", "ledger", r["_bad"]))
            continue
        label = "%s :: %s" % (r.get("target") or "?", r.get("section") or "(no heading)")
        missing = [k for k in ("target", "bytes", "sha256", "body_b64") if k not in r]
        if missing:
            out.append(("fail", label, "record on line %s lacks %s"
                        % (r.get("_line"), ", ".join(missing))))
            continue
        try:
            want = base64.b64decode(r["body_b64"], validate=True)
        except Exception as e:
            out.append(("fail", label, "body_b64 on line %s will not decode: %s"
                        % (r["_line"], e)))
            continue
        # The ledger is checked against ITSELF before it is believed about a file.
        # A record whose bytes disagree with its own length or sha256 cannot be
        # used to accuse a file of anything.
        if len(want) != r["bytes"] or hashlib.sha256(want).hexdigest() != r["sha256"]:
            out.append(("fail", label, "ledger record on line %s is internally "
                        "inconsistent: its bytes do not match its own length/sha256"
                        % r["_line"]))
            continue
        if last[(r["target"], r.get("section") or r["sha256"])] != i:
            out.append(("superseded", label, "line %s retired by a later write to the "
                        "same heading" % r["_line"]))
            continue
        blob = read_bytes(r["target"])
        if blob is False:
            out.append(("skip", label, "target is outside this repo -- not graded"))
            continue
        if blob is None:
            out.append(("fail", label, "the target no longer exists; a block was "
                        "recorded as landing in it"))
            continue
        if want in blob:
            out.append(("ok", label, "%d bytes still present byte-for-byte" % len(want)))
            continue
        shadow = heredoc_shadow(want)
        sig = ""
        if shadow != want and shadow in blob:
            sig = (" COMMAND-SUBSTITUTION SIGNATURE CONFIRMED: the block is present "
                   "with every `...` and $(...) span REMOVED -- this is the "
                   "unquoted-heredoc defect (L-403/L-405), not an ordinary edit.")
        out.append(("fail", label, "the %d recorded bytes are NO LONGER present in %s.%s"
                    % (len(want), r["target"], sig)))
    return out


def orphan_verdict(records, head_bytes):
    """ORPHAN LEDGER ROWS: a row COMMITTED at HEAD whose block is NOT at HEAD.

    append_block.py writes the ledger row and leaves committing to the caller --
    correctly, because standing rule 10 reserves every commit to the caller. So an
    agent that appends and then commits ONLY its target file leaves the row behind,
    and an agent that commits only the LEDGER publishes a claim that a block landed
    when it did not.  Found live by a cfd lane 2026-08-30.

    THE WINDOW BETWEEN APPEND AND COMMIT IS LEGITIMATE AND MUST STAY SILENT. A row
    that is not yet at HEAD is IN FLIGHT, not orphaned, and grading it would make
    this clause fire on every correct workflow -- the false-positive shape that gets
    a guard switched off for being noisy (COMMIT_INTEGRITY_STANDARD Amendment 5
    limb C).  So the population is exactly THE ROWS COMMITTED AT HEAD, and the
    proposition is: `a committed row's block is in the target AT HEAD`.

    head_bytes(target) -> bytes   the target's bytes at HEAD
                       -> None    the target is not at HEAD -> FAIL (orphan)
                       -> False   out of this repo           -> not graded
    """
    out = []
    for r in records:
        if r.get("_bad"):
            out.append(("fail", "ledger line %s" % r.get("_line"),
                        "unparseable at HEAD: %s" % r["_bad"]))
            continue
        label = "%s :: %s" % (r.get("target", "?"), (r.get("section") or "")[:60])
        try:
            want = base64.b64decode(r.get("body_b64", ""))
        except Exception as exc:
            out.append(("fail", label, "body_b64 does not decode at HEAD: %s" % exc))
            continue
        blob = head_bytes(r.get("target", ""))
        if blob is False:
            out.append(("skip", label, "target is outside this repo -- not graded"))
            continue
        if blob is None:
            out.append(("fail", label,
                        "ORPHAN: this row is COMMITTED but its target is NOT AT HEAD. "
                        "The ledger claims a block landed in a file the repository "
                        "does not have."))
            continue
        if want in blob:
            out.append(("ok", label, "%d bytes present at HEAD" % len(want)))
        else:
            out.append(("fail", label,
                        "ORPHAN: this row is COMMITTED but its %d recorded bytes are "
                        "NOT in %s AT HEAD. The row was committed without its block."
                        % (len(want), r.get("target"))))
    return out



def check_numerics_index():
    """[5/5] Is the NUMERICS_KNOWLEDGE FAMILY INDEX still true of its own tail?

    The index is a DERIVED value. A derived value maintained by hand drifts, and
    on 2026-08-30 it had: N-C listed as N-C1 alone against an actual N-C7, N-AV to
    11 against an actual 13 -- 8 entries, with FIVE of seven families correct and
    the only two stale being the two that had grown. Deriving it removes the
    drift; this clause makes a future drift impossible to accumulate silently.
    """
    print("\n[5/5] NUMERICS INDEX -- is the FAMILY INDEX true of its own tail?")
    try:
        sys.path.insert(0, os.path.join(REPO, "scripts"))
        import check_numerics_index as nk
        div = nk.divergence(os.path.join(REPO, "docs", "NUMERICS_KNOWLEDGE.md"))
    except Exception as exc:
        warn("numerics-index", "NOT MEASURED -- the checker could not run (%s). "
             "A zero from an instrument that did not run is not evidence." % exc)
        return
    if div and div[0][0] == "*":
        fail("numerics-index", "no FAMILY INDEX block exists in the file at all")
        return
    if not div:
        ok("numerics-index", "the index lists exactly the ids in the tail")
        return
    for k, miss, extra, _ in div:
        fail("numerics-index",
             "N-%s DIVERGES: %d id(s) in the tail are MISSING from the index %s; "
             "%d listed that are not in the tail %s. Regenerate with "
             "`scripts/check_numerics_index.py --gen` and append a SUPERSEDING "
             "block -- never edit above, this file is cited by line number."
             % (k, len(miss), ["N-%s%d" % (k, x) for x in miss],
                len(extra), ["N-%s%d" % (k, x) for x in extra]))


def check_provenance(strict=False):
    print("\n[4/5] PROVENANCE -- do recorded blocks still match their source bytes?")
    path = os.path.join(REPO, *PROV_LEDGER_REL.split("/"))
    recs = load_provenance(path)

    def not_measured(why):
        (fail if strict else warn)(
            "provenance",
            "NOT MEASURED -- %s. This clause graded 0 blocks and is a DEAD LEVER "
            "until append_block.py is the path record appends take. A green here "
            "would mean nothing." % why)
        print("  ....  CANNOT SEE: any block written by hand, by heredoc, or by any "
              "path other than append_block.py. OWNER verification-supervisor; "
              "RE-READ 2026-09-30 to re-measure the population.")

    # THE TWO ZERO-POPULATION CASES ARE NOT THE SAME CASE, and collapsing them is
    # the fail-open this clause exists to avoid (verification-supervisor,
    # 2026-08-30, on landing). NO LEDGER AT ALL is the honest day-one state: the
    # recorder has never run, nothing is claimed, and a warning is the truthful
    # report. A LEDGER THAT EXISTS AND GRADES NOTHING is a different proposition
    # -- the recorder DID run, and every record it wrote has since become
    # ungradeable. That is indistinguishable from the recorder being silently
    # broken, and it is exactly the shape of the five fail-opens this team has
    # already measured (queue_entry_check with no args returns rc 0; the
    # reconciler's DEFAULT_PATHS; append_record.py's `if new_ids:`). So it FAILS
    # on its own, without waiting for --strict-provenance to be armed.
    if recs is None:
        not_measured("no ledger at %s -- the recorder has never run" % PROV_LEDGER_REL)
        return
    if not recs:
        fail("provenance",
             "the ledger at %s EXISTS but holds 0 records. The recorder ran and "
             "wrote nothing gradeable; a green here would be indistinguishable "
             "from a silently broken recorder." % PROV_LEDGER_REL)
        return

    def read_bytes(target):
        if os.path.isabs(target):
            return False
        p = os.path.join(REPO, *target.split("/"))
        if not os.path.exists(p):
            return None
        with open(p, "rb") as fh:
            return fh.read()

    graded = 0
    for status, label, msg in provenance_verdict(recs, read_bytes):
        if status == "fail":
            fail("provenance", "%s -- %s" % (label, msg)); graded += 1
        elif status == "ok":
            ok("provenance", "%s -- %s" % (label, msg)); graded += 1
        else:
            print("  ....  %-14s %s -- %s" % ("provenance", label, msg))
    if graded == 0:
        # Same ruling as above: the ledger EXISTS, so this is not day one.
        fail("provenance",
             "the ledger holds %d record(s) and NONE was graded -- all are "
             "superseded or out of repo. The clause measured nothing while "
             "appearing to run." % len(recs))
    else:
        print("  ....  population: %d of %d ledger record(s) graded" % (graded, len(recs)))

    # --- ORPHAN PASS: rows COMMITTED at HEAD whose block is not at HEAD ---------
    def _head(path):
        p = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + path],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return p.stdout if p.returncode == 0 else None

    led_at_head = _head(PROV_LEDGER_REL)
    if led_at_head is None:
        print("  ....  ORPHAN PASS: the ledger is not at HEAD -- every row is IN "
              "FLIGHT, nothing to grade. Not a failure.")
        return
    head_recs, bad = [], 0
    for n, raw in enumerate(led_at_head.splitlines(), 1):
        if not raw.strip():
            continue
        try:
            head_recs.append(json.loads(raw.decode("utf-8")))
        except Exception as exc:
            head_recs.append({"_bad": str(exc), "_line": n}); bad += 1
    inflight = max(0, len(recs) - len(head_recs))

    def head_bytes(target):
        if not target or os.path.isabs(target):
            return False
        return _head(target)

    o_graded = 0
    for status, label, msg in orphan_verdict(head_recs, head_bytes):
        if status == "fail":
            fail("orphan-row", "%s -- %s" % (label, msg)); o_graded += 1
        elif status == "ok":
            o_graded += 1
        else:
            pass
    print("  ....  ORPHAN PASS: %d committed row(s) checked against HEAD, %d in "
          "flight (append not yet committed -- legitimate, not graded)%s"
          % (o_graded, inflight, ", %d unparseable" % bad if bad else ""))


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


# (label, territory_sha, territory_dt, section_sha, section_dt, stamp_dt, want)
# dt values are seconds relative to an arbitrary territory-commit instant T.
FRESHNESS_CASES = [
    # -- PRIMARY: commit to commit --------------------------------------------
    ("same commit",        "aaaa", 0, "aaaa",    0, -300, "ok"),
    ("board after work",   "aaaa", 0, "bbbb",  +87, -300, "ok"),
    ("board before work",  "aaaa", 0, "bbbb", -3600, -3600, "stale"),
    # -- FALLBACK: hand stamp, minute resolution ------------------------------
    # THE BUG: stamp typed 20:55Z, commit-tree ran at 20:56:27.
    ("minute-res stamp",   "aaaa", 0, None,   None,  -87, "ok"),
    ("stamp genuinely old","aaaa", 0, None,   None, -2400, "stale"),
    ("stamp exactly at tolerance", "aaaa", 0, None, None, -600, "ok"),
    ("stamp just past tolerance",  "aaaa", 0, None, None, -601, "stale"),
    # -- degenerate -----------------------------------------------------------
    ("no territory commits", None, None, None, None, -300, "ok"),
    ("no stamp, no section", "aaaa", 0, None, None, None, "ok"),
]


def _prov_write_real(d, when, target=None):
    """Drive the REAL producer: scripts/append_block.py, as a subprocess.

    BIRTH REQUIREMENT (VERIFICATION_CHARTER §2j.2): ask who wrote the bytes the
    control reads. A hand-built ledger fixture proves only that the parser
    parses -- it cannot prove the clause grades what the tool actually emits, and
    a control the harness wrote for itself is not a control. So this limb writes
    nothing itself: it runs append_block.py and grades ITS ledger line.

    The body carries BOTH shapes an unquoted heredoc destroys -- a backtick pair
    and a $(...) -- and both must survive verbatim into the record.
    """
    tgt = target or os.path.join(d, "board.md")
    if not os.path.exists(tgt):
        with open(tgt, "w") as fh:
            fh.write("# Board\n\nprior content that must not move\n")
    body = os.path.join(d, "body_%s.md" % when.replace(":", ""))
    with open(body, "wb") as fh:
        fh.write(b"\n## verification\n\n"
                 b"**Section last written:** @@WHEN@@ by verification-supervisor.\n"
                 b"The verdict word is `GATE FAIL` and the queue key is `Queue:`.\n"
                 b"A command substitution that must NOT run: $(date -u).\n")
    led = os.path.join(d, "prov.jsonl")
    r = subprocess.run(
        [sys.executable, os.path.join(REPO, "scripts", "append_block.py"),
         "--target", tgt, "--body", body, "--subst", "WHEN=" + when],
        capture_output=True, text=True,
        env=dict(os.environ, APPEND_BLOCK_LEDGER=led))
    return tgt, led, r.returncode


def provenance_selftest():
    """Planted controls for the provenance clause (CLAUDE.md rule 3).

    Every limb states what it plants and whether it must SPEAK or stay SILENT. A
    clause that only ever fires on a fixture it built is not evidence, so limb 1
    runs the real tool; the negative limbs exist because a checker that flags a
    correct write is the defect this file has already shipped twice.
    """
    import shutil
    import tempfile
    bad, n = 0, 0
    d = tempfile.mkdtemp(prefix="prov_")

    def grade(label, records, reader, want_statuses, want_sig=None):
        nonlocal bad, n
        n += 1
        if records is None:
            # Found by mutation test M5 (recorder disabled): a limb with no ledger
            # to read used to raise TypeError. A control that CRASHES reports
            # nothing -- it must fail loudly and let the remaining limbs run.
            print("  FAIL  selftest    %-28s no ledger to grade (records is None)"
                  % label); bad += 1
            return
        got = provenance_verdict(records, reader)
        statuses = [s for s, _, _ in got]
        msgs = " | ".join(m for _, _, m in got)
        problem = None
        if statuses != want_statuses:
            problem = "got %s want %s" % (statuses, want_statuses)
        elif want_sig is not None:
            has = "SIGNATURE CONFIRMED" in msgs
            if has != want_sig:
                problem = "signature %s, wanted %s" % (has, want_sig)
        if problem:
            print("  FAIL  selftest    %-28s %s" % (label, problem)); bad += 1
        else:
            print("  ok    selftest    %-28s %s" % (label, "/".join(statuses) or "-"))

    abs_reader = lambda t: (open(t, "rb").read() if os.path.exists(t) else None)

    # --- LIMB 1 (REAL PATH, must be SILENT: an unmodified block is not flagged) --
    tgt, led, rc = _prov_write_real(d, "2026-08-30T01:00Z")
    n += 1
    recs = load_provenance(led)
    if rc != 0 or not recs:
        print("  FAIL  selftest    %-28s append_block.py rc=%s, %s record(s)"
              % ("real path writes a record", rc, 0 if not recs else len(recs))); bad += 1
    else:
        planted = base64.b64decode(recs[0]["body_b64"])
        landed = open(tgt, "rb").read()
        miss = [p for p in (b"`GATE FAIL`", b"`Queue:`", b"$(date -u)",
                            b"2026-08-30T01:00Z")
                if p not in planted or p not in landed]
        if miss:
            print("  FAIL  selftest    %-28s did not survive: %s"
                  % ("real path keeps both shapes", miss)); bad += 1
        else:
            print("  ok    selftest    %-28s backtick pair + $(...) verbatim in "
                  "record AND file" % "real path keeps both shapes")
    grade("unmodified block SILENT", recs, abs_reader, ["ok"])

    # --- LIMB 2 (SILENT): an unrelated append below must not disturb the block ---
    with open(tgt, "ab") as fh:
        fh.write(b"\n## some other team\n\nlater, unrelated work\n")
    grade("append below SILENT", load_provenance(led), abs_reader, ["ok"])

    # --- LIMB 3 (must SPEAK): the heredoc mutation, applied to the landed file ---
    keep = open(tgt, "rb").read()
    with open(tgt, "wb") as fh:
        fh.write(heredoc_shadow(keep))
    grade("heredoc mutation SPEAKS", load_provenance(led), abs_reader, ["fail"],
          want_sig=True)

    # --- LIMB 4 (must SPEAK): one byte, INSIDE the block and outside any backtick
    # span, so the clause must fail on it WITHOUT claiming the heredoc signature.
    # Sensitivity has to be byte-level, not signature-level, or the clause would
    # only ever catch the one defect it was written for.
    flipped = keep.replace(b"the queue key", b"the queve key", 1)
    assert flipped != keep, "limb 4 planted nothing"
    with open(tgt, "wb") as fh:
        fh.write(flipped)
    grade("one-byte flip SPEAKS", load_provenance(led), abs_reader, ["fail"],
          want_sig=False)
    with open(tgt, "wb") as fh:
        fh.write(keep)

    # --- LIMB 5 (SILENT): supersession, i.e. the real board-rewrite protocol -----
    # A second write to the same `## verification` heading retires the first. The
    # file then carries ONLY the newer block, exactly as a board rebuild leaves it.
    _prov_write_real(d, "2026-08-30T02:00Z", target=tgt)
    recs2 = load_provenance(led)
    if not recs2:
        # Also M5: without a ledger the remaining limbs have nothing to plant into.
        # Stop and SAY so; never let a limb pass because it could not run.
        print("  FAIL  selftest    %-28s no ledger after a real-path write -- limbs "
              "5-10 could not be planted" % "supersession SILENT"); bad += 1; n += 1
        shutil.rmtree(d, ignore_errors=True)
        return bad, n
    newer = base64.b64decode(recs2[-1]["body_b64"])
    with open(tgt, "wb") as fh:
        fh.write(b"# Board\n\nprior content that must not move\n" + newer)
    grade("supersession SILENT", recs2, abs_reader, ["superseded", "ok"])

    # --- LIMB 6 (must SPEAK): a ledger that disagrees with itself ----------------
    tampered = dict(recs2[-1]); tampered["sha256"] = "0" * 64
    grade("ledger self-inconsistent SPEAKS", [tampered], abs_reader, ["fail"])

    # --- LIMB 7 (must SPEAK): the block's file is gone ---------------------------
    grade("target deleted SPEAKS", [recs2[-1]], lambda t: None, ["fail"])

    # --- LIMB 8 (must NOT be graded): a record pointing outside the repo ---------
    grade("out-of-repo record NOT graded", [recs2[-1]], lambda t: False, ["skip"])

    # --- LIMB 9 (must SPEAK): a corrupt ledger line is reported, never raised ----
    with open(os.path.join(d, "bad.jsonl"), "w") as fh:
        fh.write("{not json\n")
    grade("corrupt ledger line SPEAKS",
          load_provenance(os.path.join(d, "bad.jsonl")), abs_reader, ["fail"])

    # --- LIMB 10 (the fail-open guard): an empty population is NEVER ok ----------
    n += 1
    absent = load_provenance(os.path.join(d, "nope.jsonl"))
    with open(os.path.join(d, "empty.jsonl"), "w") as fh:
        fh.write("\n")
    empty = load_provenance(os.path.join(d, "empty.jsonl"))
    if absent is not None or empty != []:
        print("  FAIL  selftest    %-28s absent=%r empty=%r -- an unseeable "
              "population must be distinguishable from a clean one"
              % ("empty population NOT green", absent, empty)); bad += 1
    else:
        print("  ok    selftest    %-28s absent and empty both reportable as "
              "NOT MEASURED" % "empty population NOT green")

    # --- LIMBS 11-14: THE ORPHAN PASS -------------------------------------------
    # A row COMMITTED at HEAD whose block is not at HEAD. The IN-FLIGHT window
    # (appended, not yet committed) is legitimate and is excluded by POPULATION
    # rather than by a verdict -- limb 14 drives that through a REAL git repo so
    # the exclusion is demonstrated, not asserted (charter 2j.2).
    def ograde(label, records, reader, want_statuses):
        nonlocal bad, n
        n += 1
        got = orphan_verdict(records, reader)
        statuses = [s for s, _, _ in got]
        if statuses != want_statuses:
            print("  FAIL  selftest    %-28s wanted %r got %r -- %s"
                  % (label, want_statuses, statuses,
                     " | ".join(m for _, _, m in got))); bad += 1
        else:
            print("  ok    selftest    %-28s %s" % (label, "/".join(statuses)))

    body = b"\n## orphan probe\n\na `backtick` and a $(paren)\n"
    row = dict(target="docs/PROBE.md", section="orphan probe",
               body_b64=base64.b64encode(body).decode())
    ograde("orphan row SPEAKS", [row], lambda t: b"other content entirely", ["fail"])
    ograde("orphan target gone SPEAKS", [row], lambda t: None, ["fail"])
    ograde("landed row SILENT", [row], lambda t: b"before" + body + b"after", ["ok"])
    ograde("orphan out-of-repo NOT graded", [row], lambda t: False, ["skip"])

    # LIMB 15, THE REAL ONE: a genuine git repository, a real commit of the LEDGER
    # ONLY, and the orphan detected through `git show HEAD:` -- not a lambda.
    n += 1
    g = os.path.join(d, "orepo")
    os.makedirs(g)
    def _g(*a):
        return subprocess.run(["git", "-C", g] + list(a),
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    _g("init", "-q", "-b", "main", "."); _g("config", "user.email", "s@l")
    _g("config", "user.name", "s")
    with open(os.path.join(g, "seed.txt"), "w") as fh:
        fh.write("seed\n")
    _g("add", "seed.txt"); _g("commit", "-qm", "seed")
    # the block is written to the target but ONLY the ledger is committed
    with open(os.path.join(g, "PROBE.md"), "wb") as fh:
        fh.write(b"header\n" + body)
    with open(os.path.join(g, "led.jsonl"), "w") as fh:
        fh.write(json.dumps(dict(target="PROBE.md", section="orphan probe",
                                 body_b64=base64.b64encode(body).decode())) + "\n")
    _g("add", "led.jsonl"); _g("commit", "-qm", "ledger only, target left behind")
    def real_head(target):
        p = _g("show", "HEAD:" + target)
        return p.stdout if p.returncode == 0 else None
    led = _g("show", "HEAD:led.jsonl").stdout
    rrows = [json.loads(l.decode()) for l in led.splitlines() if l.strip()]
    rstat = [s for s, _, _ in orphan_verdict(rrows, real_head)]
    if rstat == ["fail"]:
        print("  ok    selftest    %-28s a real ledger-only commit is caught "
              "through git show HEAD:" % "REAL orphan commit SPEAKS")
    else:
        print("  FAIL  selftest    %-28s wanted ['fail'] got %r"
              % ("REAL orphan commit SPEAKS", rstat)); bad += 1
    # and once the target lands, the SAME rows must go silent -- proving the clause
    # tracks the repository rather than merely always complaining.
    n += 1
    _g("add", "PROBE.md"); _g("commit", "-qm", "the target lands")
    rstat2 = [s for s, _, _ in orphan_verdict(rrows, real_head)]
    if rstat2 == ["ok"]:
        print("  ok    selftest    %-28s the same rows go SILENT once the target "
              "is committed" % "REAL orphan CLEARS")
    else:
        print("  FAIL  selftest    %-28s wanted ['ok'] got %r"
              % ("REAL orphan CLEARS", rstat2)); bad += 1

    shutil.rmtree(d, ignore_errors=True)
    return bad, n


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
    # ---- freshness decision, the half that was systematically wrong ----
    T = 1_800_000_000
    for label, tsha, tdt, ssha, sdt, stdt, want in FRESHNESS_CASES:
        tt = None if tdt is None else T + tdt
        st = None if sdt is None else T + sdt
        stamp_t = None if stdt is None else T + stdt
        got, reason = freshness_verdict(tsha, tt, ssha, st, stamp_t)
        if got != want:
            print("  FAIL  selftest    %-28s got %s want %s (%s)"
                  % (label, got, want, reason)); bad += 1
        else:
            print("  ok    selftest    %-28s %s" % (label, got))

    # ---- lane frontmatter: `tools` only where a lane is declared RESTRICTED ----
    # Added 2026-08-24 with the ansys-verification team, the first team with lane
    # types of its own and the first RESTRICTED lane (haiku: Bash, Read, Grep,
    # Glob; no Edit/Write). The generator must refuse `tools` on a supervisor or
    # an unrestricted lane (an explicit list silently drops the Agent tool), and
    # must refuse a restricted lane that is missing its list or grants a writer.
    sys.path.insert(0, os.path.join(REPO, "harness"))
    import generate_agents as ga
    fm = ga.frontmatter
    LANE_CASES = [
        # (label, filename, content, tools_allowed, want_ok)
        ("supervisor no tools", "x-supervisor.md", fm("x-supervisor", "d: e", "fable"), False, True),
        ("supervisor with tools", "x-supervisor.md",
         fm("x-supervisor", "d: e", "fable", ["Bash"]), False, False),
        ("restricted lane ok", "x-lane-haiku.md",
         fm("x-lane-haiku", "d", "haiku", ["Bash", "Read", "Grep", "Glob"]), True, True),
        ("restricted lane missing list", "x-lane-haiku.md",
         fm("x-lane-haiku", "d", "haiku"), True, False),
        ("restricted lane grants Edit", "x-lane-haiku.md",
         fm("x-lane-haiku", "d", "haiku", ["Bash", "Edit"]), True, False),
        ("restricted lane grants Agent", "x-lane-haiku.md",
         fm("x-lane-haiku", "d", "haiku", ["Bash", "Agent"]), True, False),
        ("full model id parses", "x-lane-opus48.md",
         fm("x-lane-opus48", "d", "claude-opus-4-8"), False, True),
        ("name mismatch", "y.md", fm("x", "d", "opus"), False, False),
    ]
    for label, fname, content, allowed, want_ok in LANE_CASES:
        problem = ga.assert_parses(fname, content, allowed)
        got_ok = problem is None
        if got_ok != want_ok:
            print("  FAIL  selftest    %-28s got %s want %s (%s)"
                  % (label, "ok" if got_ok else "reject", "ok" if want_ok else "reject",
                     problem)); bad += 1
        else:
            print("  ok    selftest    %-28s %s" % (label, "ok" if got_ok else "rejected"))
    # A team may carry its own lane cap; the default is the charter's 3. The
    # cap is rendered, not enforced (SUPERVISION_CHARTER v1.4 §8 says so).
    cfg = load_cfg()
    for t in cfg["teams"]:
        cap = t.get("max_live_lanes", cfg["defaults"]["max_live_lanes"])
        if cap != cfg["defaults"]["max_live_lanes"] and not t.get("lane_cap_note"):
            print("  FAIL  selftest    %-28s cap %d differs from default %d with no "
                  "lane_cap_note naming the authority"
                  % (t["team"], cap, cfg["defaults"]["max_live_lanes"])); bad += 1
        else:
            print("  ok    selftest    %-28s lane cap %d%s"
                  % (t["team"], cap, "" if cap == cfg["defaults"]["max_live_lanes"]
                     else " (exception, authority recorded)"))

    # ---- provenance: does a recorded block still match its source bytes? ----
    prov_bad, prov_n = provenance_selftest()
    bad += prov_bad

    total = (len(STAMP_CASES) + 2 + len(FRESHNESS_CASES) + len(LANE_CASES)
             + len(cfg["teams"]) + prov_n)
    print("\n%s: harness selftest, %d case(s), %d failure(s)"
          % ("FAIL" if bad else "PASS", total, bad))
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
    ap.add_argument("--strict-provenance", action="store_true",
                    help="make an unmeasurable provenance population a FAIL rather "
                         "than a NOT MEASURED warning (arm once the ledger is fed)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    cfg = load_cfg()
    check_roster()
    secs = check_board(cfg, args.worktree)
    check_freshness(cfg, secs)
    check_provenance(args.strict_provenance)
    check_numerics_index()

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
