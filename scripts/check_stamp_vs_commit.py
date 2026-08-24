#!/usr/bin/env python3
"""Fire when an in-record stamp was written AHEAD of the wall clock.

    python3 scripts/check_stamp_vs_commit.py              # report-only sweep, exit 0
    python3 scripts/check_stamp_vs_commit.py --strict     # exit 1 on any FIRE
    python3 scripts/check_stamp_vs_commit.py --at <sha>   # grade a committed tree
    python3 scripts/check_stamp_vs_commit.py --selftest   # planted controls C1-C6
    python3 scripts/check_stamp_vs_commit.py --show-all   # list every graded stamp

THE DEFECT CLASS. `bd3edfe8` (2026-08-22T21:00:24Z) is the ancestor: an
instrument comparing a hand-typed stamp against a machine timestamp, wrong
because the hand-typed side was not read from a clock. Its second face is a
stamp typed LATER than the moment it claims to describe -- a record dated into
the future. On 2026-08-23 that happened three times in one evening: closure's
board, the verification board (21:04/21:15/21:20/21:35/21:38/21:40Z, all typed
before ~21:13Z), and the D473 docket row. The rule adopted in response is that a
stamp is written only from a `date -u` read in the SAME shell invocation as the
write. This is the machine check for it: for every stamped line, find the commit
that introduced the line and compare the stamp to that commit's committer date.

THE SKEW MODEL IS SHARED, ONE MODEL, TWO DIRECTIONS -- see `scripts/stamp_skew.py`.
This check imports its tolerances; it defines none of its own, and the stale-side
tolerance still has exactly one definition, in `check_harness.py`. If that import
breaks, both this check and the shared module REFUSE (exit 2) rather than
substituting a second copy of a number.

    FORWARD_TOLERANCE_S = 60 s, and a fire is delta STRICTLY GREATER than it.

  WHY 60 s -- MECHANISM, THEN MEASUREMENT. Only one mechanism puts an honest
  stamp after its own committer date: the writer reads `date -u`, then rounds the
  minute up when typing (clock 20:04:54, stamp `20:05Z`). The read precedes the
  commit, so the lead is bounded by the rounding, and rounding to the next whole
  minute is bounded by 60 s. The slow-CAS-retry story runs the other way -- a
  retry re-runs `commit-tree` and pushes the committer date LATER, making the
  delta more negative. MEASURED 2026-08-24 over the ADDED corpus lines of the
  last 300 commits (added lines, so the introducing commit is exact -- no blame
  heuristic): 400 UTC-marked stamps graded, 76 positive. Benign cluster: +6, +6,
  +49, +49 s, all minute-rounding, all inside 60 s. Next value up: +70 s. Every
  row at or above +70 s is either inside the 2026-08-22/23 window the board has
  itself disclosed as estimated stamps, or in the future-intent class below.
  Nothing benign sits between 60 and 70 s, so bound and data agree.

SCOPE, and what is deliberately NOT graded -- stated, never silent:

  GRADED   a token carrying an explicit UTC marker: `YYYY-MM-DD` then `T` or a
           space, `HH:MM`, optional `:SS(.frac)`, optional range tail
           (`-HH:MM`, en/em dash or arrow), then `Z` or `UTC`. Also a full ISO
           token with a numeric offset whose hour part is <= 14 (a real zone
           offset), converted to UTC. For a range, the START is graded.

  UNMARKED a date+time with no `Z`, no `UTC` and no offset. NOT graded, COUNTED
           and listed under `--show-all`. Evidence for the exclusion: in this
           corpus these tokens are file mtimes, ctimes, run start times and
           quoted commit dates -- `T3_RESULTS.md` run rows, `DOCKET.md` mtime
           forensics, `LESSONS.md` commit citations. A local-or-unspecified time
           cannot be compared to an instant, and an mtime is legitimately any
           value. 28 of 428 tokens on added corpus lines in the 300-commit scan.

  PLANNED  a graded stamp whose 80 preceding characters carry a future-intent
           cue (`ETA`, `<=`/`≤`, `deadline`, `planned`, `schedul`, `expect`,
           `projec`, `forecast`, `critical path`, `pacing`, `no later than`).
           A legitimately future-dated time -- `R_f ETA <= 2026-08-25T14:54Z` --
           is not this defect. Reported with its delta so the exclusion is
           visible, but never a FIRE. This is a HEURISTIC and the cue list is the
           instrument's escape hatch: it is printed by `--cues` and any row it
           suppresses is still shown in the table.

  REFUSAL  a token that DOES carry a UTC marker or an offset but whose fields do
           not form a valid instant (month 13, hour 25, minute 60) is a
           CANNOT-PARSE refusal, exit 2. It is never silently skipped -- a reader
           that cannot see a stamp must say so, not shrug (rule 3).

ATTRIBUTION. The introducing commit is taken from `git blame -w --line-porcelain`
at the graded revision. Blame names the commit that LAST TOUCHED the line, which
for a reflowed or moved line can be later than the commit that first wrote the
stamp. That error is conservative in the safe direction: a later committer date
makes the delta smaller and the check quieter, so blame can hide a fire but
cannot manufacture one. `--at <sha>` grades a committed tree, which is how a
historical instance is reproduced.

KNOWN FALSE-POSITIVE CLASS, disclosed rather than engineered away: a genuinely
future-dated time written without a cue word (a progress-table ETA rendered as
`**~2026-08-23 01:40Z**`) reads as a FIRE. Triage the fire; do not widen the
cue list to make a red go away.

EXIT CODES.  0 report ran (or --strict with no fire).  1 --strict with >= 1 FIRE,
or a selftest control failed.  2 REFUSAL: CANNOT-PARSE, a blame/ls-tree failure,
or the shared skew model unavailable.
"""

import argparse
import datetime
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    import stamp_skew
except Exception as exc:                            # pragma: no cover - refusal path
    sys.stderr.write("REFUSAL: shared skew model unavailable: %s\n" % exc)
    sys.exit(2)

FORWARD_TOLERANCE_S = stamp_skew.FORWARD_TOLERANCE_S

# ---------------------------------------------------------------- corpus ----

GLOBS = ("docs/LAB_STATE.md", "docs/DOCKET.md", "docs/LESSONS.md",
         "docs/COST_CALIBRATION.md", "docs/*_AUDIT.md")
SUFFIXES = ("_RESULTS.md", "_PREREGISTRATION.md")
ROOTS = ("cases/", "docs/", "verification/")


def in_corpus(path):
    for g in GLOBS:
        if fnmatch.fnmatch(path, g):
            return True
    return path.endswith(SUFFIXES) and path.startswith(ROOTS)


# ----------------------------------------------------------------- stamps ---

_SEP = r"[-–—→>]"          # hyphen, en dash, em dash, arrow
TOKEN_RE = re.compile(
    r"(?P<Y>\d{4})-(?P<M>\d{2})-(?P<D>\d{2})[T ]"
    r"(?P<h>\d{2}):(?P<mi>\d{2})(?::(?P<s>\d{2})(?:\.\d+)?)?"
    r"(?:\s*" + _SEP + r"\s*\d{2}:\d{2}(?::\d{2})?)?"
    r"(?:\s*(?P<mark>Z|UTC)\b|(?P<off>[+-]\d{2}:?\d{2}))?")

CUES = re.compile(
    r"(?i)(\bETA\b|≤|<=|no later than|\bdeadline|\bplanned\b|\bschedul"
    r"|\bexpect|\bprojec|\bforecast|critical path|\bpacing\b)")
CUE_WINDOW = 80

GRADED, UNMARKED, BAD = "graded", "unmarked", "bad"


class CannotParse(Exception):
    """A token that looks like a stamp and carries a UTC marker, but is not one."""


def stamps_in(line):
    """Yield (token, start_col, epoch_or_None, kind) for every candidate token."""
    out = []
    for m in TOKEN_RE.finditer(line):
        mark, off = m.group("mark"), m.group("off")
        tok = m.group(0)
        if not mark and not off:
            out.append((tok, m.start(), None, UNMARKED))
            continue
        if off and not mark and int(off[1:3]) > 14:
            # `22:00-22:04Z` style range read as an offset: not a real zone.
            out.append((tok, m.start(), None, UNMARKED))
            continue
        try:
            dt = datetime.datetime(
                int(m.group("Y")), int(m.group("M")), int(m.group("D")),
                int(m.group("h")), int(m.group("mi")), int(m.group("s") or 0),
                tzinfo=datetime.timezone.utc)
        except ValueError:
            out.append((tok, m.start(), None, BAD))
            continue
        if off and not mark:
            oh, om = int(off[1:3]), int(off[-2:])
            shift = datetime.timedelta(hours=oh, minutes=om)
            dt = dt - shift if off[0] == "+" else dt + shift
        out.append((tok, m.start(), dt.timestamp(), GRADED))
    return out


def is_planned(line, col):
    return bool(CUES.search(line[max(0, col - CUE_WINDOW):col]))


# -------------------------------------------------------------------- git ---

def git(repo, *args, **kw):
    p = subprocess.run(("git", "-C", repo) + args, capture_output=True, text=True)
    if p.returncode != 0 and not kw.get("allow_fail"):
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr.strip()))
    return p.stdout


def tree_files(repo, rev):
    return [p for p in git(repo, "ls-tree", "-r", "--name-only", rev).splitlines()
            if in_corpus(p)]


def blob_lines(repo, rev, path):
    return git(repo, "show", "%s:%s" % (rev, path)).split("\n")


def blame(repo, rev, path, linenos):
    """{lineno: (sha, committer_epoch)} for the given lines at `rev`."""
    got = {}
    linenos = sorted(set(linenos))
    for i in range(0, len(linenos), 150):
        chunk = linenos[i:i + 150]
        args = ["blame", "-w", "--line-porcelain"]
        for n in chunk:
            args += ["-L", "%d,%d" % (n, n)]
        args += [rev, "--", path]
        out = git(repo, *args)
        sha = final = ctime = None
        for row in out.split("\n"):
            m = re.match(r"^([0-9a-f]{40}) \d+ (\d+)", row)
            if m:
                sha, final = m.group(1), int(m.group(2))
            elif row.startswith("committer-time "):
                ctime = int(row.split()[1])
            elif row.startswith("\t") and sha is not None and ctime is not None:
                got[final] = (sha, ctime)
                sha = ctime = None
    return got


# ------------------------------------------------------------------ sweep ---

def sweep(repo, rev="HEAD", paths=None):
    """Returns (rows, counts). Raises CannotParse on a marked-but-invalid token."""
    files = paths if paths else tree_files(repo, rev)
    rows = []
    counts = dict(files=0, tokens=0, graded=0, unmarked=0, planned=0, fires=0)
    for path in sorted(files):
        lines = blob_lines(repo, rev, path)
        hits = []
        for n, line in enumerate(lines, 1):
            found = stamps_in(line)
            if not found:
                continue
            for tok, col, ts, kind in found:
                counts["tokens"] += 1
                if kind == BAD:
                    raise CannotParse(
                        "%s:%d carries a UTC-marked token that is not a valid "
                        "instant: %r -- REFUSING to skip it silently" % (path, n, tok))
                if kind == UNMARKED:
                    counts["unmarked"] += 1
                    rows.append(dict(path=path, line=n, tok=tok, kind="UNMARKED",
                                     stamp=None, sha=None, ctime=None, delta=None,
                                     text=line.strip()[:120]))
                else:
                    hits.append((n, col, tok, ts, line))
        if not hits:
            continue
        counts["files"] += 1
        att = blame(repo, rev, path, [h[0] for h in hits])
        for n, col, tok, ts, line in hits:
            if n not in att:
                raise RuntimeError("blame returned no attribution for %s:%d" % (path, n))
            sha, ctime = att[n]
            status, delta = stamp_skew.ahead_verdict(ts, ctime)
            counts["graded"] += 1
            planned = is_planned(line, col)
            if status == "ahead" and planned:
                kind = "PLANNED"
                counts["planned"] += 1
            elif status == "ahead":
                kind = "FIRE"
                counts["fires"] += 1
            else:
                kind = "ok"
            rows.append(dict(path=path, line=n, tok=tok, kind=kind, stamp=ts,
                             sha=sha, ctime=ctime, delta=delta,
                             text=line.strip()[:120]))
    return rows, counts


def iso(epoch):
    return datetime.datetime.fromtimestamp(
        epoch, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def report(rows, counts, show_all=False):
    fires = [r for r in rows if r["kind"] == "FIRE"]
    planned = [r for r in rows if r["kind"] == "PLANNED"]
    print("  scanned  %d corpus files carrying stamps, %d candidate tokens"
          % (counts["files"], counts["tokens"]))
    print("  graded   %d UTC-marked stamps against their introducing commit"
          % counts["graded"])
    print("  skipped  %d UNMARKED date+time tokens (no Z/UTC/offset -- mtimes, "
          "ctimes, run times; see header)" % counts["unmarked"])
    print("  planned  %d ahead-of-commit stamps carrying a future-intent cue "
          "(reported, never a fire)" % counts["planned"])
    print("  FIRES    %d" % counts["fires"])
    if fires:
        print("\n  %-46s %-24s %-10s %-22s %s"
              % ("file:line", "stamp", "commit", "committer date", "delta"))
        for r in sorted(fires, key=lambda r: -r["delta"]):
            print("  %-46s %-24s %-10s %-22s %+d s (%+.1f min)"
                  % ("%s:%d" % (r["path"], r["line"]), r["tok"], r["sha"][:8],
                     iso(r["ctime"]), r["delta"], r["delta"] / 60.0))
    if planned and show_all:
        print("\n  PLANNED (future-intent cue, excluded by the cue list):")
        for r in sorted(planned, key=lambda r: -r["delta"]):
            print("    %s:%d  %s  %+d s   %s"
                  % (r["path"], r["line"], r["tok"], r["delta"], r["text"][:70]))
    if show_all:
        un = [r for r in rows if r["kind"] == "UNMARKED"]
        print("\n  UNMARKED (not graded, listed so the skip is not silent): %d" % len(un))
        for r in un:
            print("    %s:%d  %s" % (r["path"], r["line"], r["tok"]))
    return fires


# --------------------------------------------------------------- controls ---

def _mkrepo(tmp, lines, cdate):
    os.makedirs(os.path.join(tmp, "docs"))
    with open(os.path.join(tmp, "docs", "LAB_STATE.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    env = dict(os.environ, GIT_AUTHOR_DATE=cdate, GIT_COMMITTER_DATE=cdate,
               GIT_AUTHOR_NAME="control", GIT_AUTHOR_EMAIL="c@x",
               GIT_COMMITTER_NAME="control", GIT_COMMITTER_EMAIL="c@x")
    for cmd in (["init", "-q", "-b", "main"], ["add", "docs/LAB_STATE.md"],
                ["commit", "-q", "-m", "control"]):
        p = subprocess.run(["git", "-C", tmp] + cmd, env=env,
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError("control repo setup failed: %s" % p.stderr)
    return tmp


CONTROL_BASE = "2026-08-24T12:00:00+00:00"


def selftest(repo, run_mutation=True):
    """Planted controls. A zero from this check is worth nothing unless the same
    reader has been SHOWN seeing a non-zero -- C1 and C5 are those non-zeros."""
    results = []

    def rec(name, ok, detail):
        results.append((name, ok, detail))
        print("  %-4s %-58s %s" % ("PASS" if ok else "FAIL", name, detail))

    # C1/C2/C3/C3b -- one planted repo, four planted lines, one commit at 12:00:00Z
    tmp = tempfile.mkdtemp(prefix="stampctl_")
    try:
        _mkrepo(tmp, [
            "## verification",
            "**Section last written:** 2026-08-24T12:30Z by C1   <- planted +1800 s",
            "**Section last written:** 2026-08-24T11:58Z by C2   <- planted -120 s",
            "**Section last written:** 2026-08-24T12:01:00Z by C3 <- planted +60 s",
            "**Section last written:** 2026-08-24T12:00:30Z by C3b <- planted +30 s",
        ], CONTROL_BASE)
        rows, counts = sweep(tmp, "HEAD")
        by_line = {r["line"]: r for r in rows if r["kind"] != "UNMARKED"}
        rec("C1 stamp 30 min AFTER committer date MUST fire",
            by_line.get(2, {}).get("kind") == "FIRE" and by_line[2]["delta"] == 1800,
            "line 2 -> %s, delta %+d s" % (by_line.get(2, {}).get("kind"),
                                           by_line.get(2, {}).get("delta", 0)))
        rec("C2 genuine stamp 2 min BEFORE must NOT fire",
            by_line.get(3, {}).get("kind") == "ok" and by_line[3]["delta"] == -120,
            "line 3 -> %s, delta %+d s" % (by_line.get(3, {}).get("kind"),
                                           by_line.get(3, {}).get("delta", 0)))
        rec("C3 stamp exactly at the forward tolerance must NOT fire",
            by_line.get(4, {}).get("kind") == "ok"
            and by_line[4]["delta"] == FORWARD_TOLERANCE_S,
            "line 4 -> %s, delta %+d s (tolerance %d s)"
            % (by_line.get(4, {}).get("kind"), by_line.get(4, {}).get("delta", 0),
               FORWARD_TOLERANCE_S))
        rec("C3b stamp inside the forward tolerance must NOT fire",
            by_line.get(5, {}).get("kind") == "ok" and by_line[5]["delta"] == 30,
            "line 5 -> %s, delta %+d s" % (by_line.get(5, {}).get("kind"),
                                           by_line.get(5, {}).get("delta", 0)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # C4 -- an unparseable stamp beside a date-like token: REFUSE, never skip
    tmp = tempfile.mkdtemp(prefix="stampctl_")
    try:
        _mkrepo(tmp, ["## verification",
                      "**Section last written:** 2026-13-45T25:99Z by C4"],
                CONTROL_BASE)
        try:
            sweep(tmp, "HEAD")
            rec("C4 unparseable UTC-marked token -> CANNOT-PARSE refusal",
                False, "sweep returned instead of refusing")
        except CannotParse as exc:
            rec("C4 unparseable UTC-marked token -> CANNOT-PARSE refusal",
                True, str(exc)[:70])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # C5 -- the known real instance, reproduced from the tree that carried it
    C5_SHA = "82194ec5"
    try:
        rows, counts = sweep(repo, C5_SHA, paths=["docs/LAB_STATE.md"])
        fires = {r["tok"]: r for r in rows if r["kind"] == "FIRE"}
        want = ("2026-08-23T21:35Z", "2026-08-23T21:40Z")
        ok = all(w in fires for w in want)
        rec("C5 real bd3edfe8-class instance at %s MUST fire" % C5_SHA, ok,
            "fired on %s" % ", ".join("%s %+d s" % (w, fires[w]["delta"])
                                      for w in want if w in fires) or "nothing")
    except Exception as exc:
        rec("C5 real bd3edfe8-class instance at %s MUST fire" % C5_SHA, False,
            "refused: %s" % str(exc)[:70])

    # C6 -- the selftest must DISCRIMINATE: every mutant drives it non-zero
    if run_mutation:
        mutants = [
            ("comparison inverted", "stamp_skew.py",
             "if delta > FORWARD_TOLERANCE_S:", "if delta < FORWARD_TOLERANCE_S:"),
            ("comparison loosened to >=", "stamp_skew.py",
             "if delta > FORWARD_TOLERANCE_S:", "if delta >= FORWARD_TOLERANCE_S:"),
            # The assignment, anchored by its own newlines: the bare string
            # `FORWARD_TOLERANCE_S = 60` also occurs in the module docstring, and
            # a first-occurrence replace mutated the PROSE and let the mutant
            # pass. Uniqueness is asserted below rather than assumed.
            ("tolerance inflated", "stamp_skew.py",
             "\nFORWARD_TOLERANCE_S = 60\n", "\nFORWARD_TOLERANCE_S = 100000\n"),
        ]
        for name, target, old, new in mutants:
            box = tempfile.mkdtemp(prefix="stampmut_")
            try:
                for f in ("check_stamp_vs_commit.py", "stamp_skew.py",
                          "check_harness.py"):
                    shutil.copy(os.path.join(_HERE, f), os.path.join(box, f))
                p = os.path.join(box, target)
                src = open(p).read()
                n_sites = src.count(old)
                if n_sites != 1:
                    rec("C6 mutant '%s' must drive the selftest non-zero" % name, False,
                        "mutation site occurs %d times, not once -- the harness is "
                        "stale, not the code" % n_sites)
                    continue
                open(p, "w").write(src.replace(old, new, 1))
                shutil.rmtree(os.path.join(box, "__pycache__"), ignore_errors=True)
                r = subprocess.run(
                    [sys.executable, "-B", os.path.join(box, "check_stamp_vs_commit.py"),
                     "--selftest", "--no-mutation", "--repo", repo],
                    capture_output=True, text=True, cwd=repo)
                rec("C6 mutant '%s' must drive the selftest non-zero" % name,
                    r.returncode != 0, "exit %d" % r.returncode)
            finally:
                shutil.rmtree(box, ignore_errors=True)

    bad = [r for r in results if not r[1]]
    print("\n  %d control(s), %d failed" % (len(results), len(bad)))
    return 1 if bad else 0


# ------------------------------------------------------------------- main ---

def find_repo(explicit):
    if explicit:
        return os.path.abspath(explicit)
    for start in (_HERE, os.getcwd()):
        p = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout.strip()
    sys.stderr.write("REFUSAL: not inside a git repository and no --repo given\n")
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--at", default="HEAD", metavar="SHA",
                    help="grade this committed tree instead of HEAD")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on any FIRE (default is a report-only sweep)")
    ap.add_argument("--selftest", action="store_true", help="run planted controls C1-C6")
    ap.add_argument("--no-mutation", action="store_true",
                    help="selftest without the C6 mutation harness (used BY C6)")
    ap.add_argument("--show-all", action="store_true",
                    help="also list PLANNED and UNMARKED rows")
    ap.add_argument("--cues", action="store_true", help="print the cue list and exit")
    ap.add_argument("--repo", default=None, help="repository root (default: discovered)")
    ap.add_argument("--path", action="append", default=None,
                    help="limit the sweep to this path (repeatable)")
    args = ap.parse_args()

    if args.cues:
        print("future-intent cue regex (%d chars of preceding context):" % CUE_WINDOW)
        print("  %s" % CUES.pattern)
        return 0

    repo = find_repo(args.repo)
    print("stamp-vs-committer-date check -- skew model: forward %d s (ahead), "
          "%d s (stale, from check_harness.py)"
          % (stamp_skew.FORWARD_TOLERANCE_S, stamp_skew.STALE_TOLERANCE_S))

    if args.selftest:
        print("\nPLANTED CONTROLS (rule 3: a zero is evidence only from a reader "
              "shown seeing a non-zero)")
        return selftest(repo, run_mutation=not args.no_mutation)

    print("  repo %s at %s\n" % (repo, args.at))
    try:
        rows, counts = sweep(repo, args.at, paths=args.path)
    except CannotParse as exc:
        sys.stderr.write("REFUSAL (CANNOT-PARSE): %s\n" % exc)
        return 2
    except RuntimeError as exc:
        sys.stderr.write("REFUSAL: %s\n" % exc)
        return 2
    fires = report(rows, counts, show_all=args.show_all)
    print("\n" + "-" * 70)
    if fires:
        print("%d stamp(s) written AHEAD of the commit that introduced them "
              "(bd3edfe8 defect class)." % len(fires))
        print("Triage each: a stamp is written only from a `date -u` read in the "
              "SAME shell invocation as the write.")
    else:
        print("No stamp in the corpus leads its introducing commit by more than "
              "%d s." % FORWARD_TOLERANCE_S)
    print("NOTE: blame attributes a line to its LAST toucher, so this check can "
          "hide a fire but cannot manufacture one.")
    return 1 if (fires and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
