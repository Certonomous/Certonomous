#!/usr/bin/env python3
"""Fire when a record was written AHEAD of the thing it claims to describe.

TWO LIMBS, ONE SWEEP, ONE TOLERANCE. Limb 1 grades STAMPS against the committer
date of the commit that introduced the stamped line. Limb 2 grades ID CITATIONS
(`L-nnn`, `Dnnn`, `C-nn`, `N-XXn`) against the committer date of the commit that
appended that id's own defining row. Both limbs share `stamp_skew`'s
FORWARD_TOLERANCE_S, share the blame attribution, and share the refusal
semantics: a token the reader cannot adjudicate is REFUSED, never skipped.

    python3 scripts/check_stamp_vs_commit.py              # report-only sweep, exit 0
    python3 scripts/check_stamp_vs_commit.py --strict     # exit 1 on any FIRE
    python3 scripts/check_stamp_vs_commit.py --at <sha>   # grade a committed tree
    python3 scripts/check_stamp_vs_commit.py --selftest   # planted controls C1-C11
    python3 scripts/check_stamp_vs_commit.py --show-all   # list every graded stamp
    python3 scripts/check_stamp_vs_commit.py --no-ids     # limb 1 only (stamps)

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

LIMB 2 -- IDS WRITTEN AHEAD OF THEIR OWN DEFINING ROW. The same defect wearing a
different coat, and its instance class is on the record: closure's board cited
`D488`/`C-15` for work that landed as `D492`/`C-18` (corrected at `8dd3f8bc`).
An id written in prose BEFORE the commit that appends that id's row is a
PREDICTION, not an identifier -- the number was guessed from a count instead of
re-derived from the tail at commit (rule 11), and it reads to any later reader as
a citation to a row that did not exist. This limb finds the commit that
introduced the CITING line and the commit that introduced the id's own DEFINING
row, and fires when the citing commit's committer date precedes the defining
commit's by more than the SAME FORWARD_TOLERANCE_S. There is no second
tolerance: `stamp_skew.ahead_verdict` is called with (defining, citing) so that
"the definition is ahead of the citation" is literally the same comparison the
stamp limb makes.

  THE FOUR FAMILIES AND THEIR DEFINING ROWS, read from the HEAD blobs 2026-08-24
  rather than assumed (counts at that HEAD in brackets):

    L-nnn  `docs/LESSONS.md`, a markdown heading `^#{1,6} L-nnn` [274 headings;
           the maximum is L-276, so the numbering has holes -- L-52 is the one
           CLAUDE.md rule 11 names, and it duly reads DANGLING below].
    Dnnn   `docs/DOCKET.md`, a table row whose FIRST CELL is the id,
           `^| [**]Dnnn[a-z][**] |` [497 rows, maximum D498]. The docket id
           carries NO HYPHEN -- `D486`, never `D-486`. `D-nnn` tokens DO occur in
           this corpus (`docs/COST_CALIBRATION.md` C-2 cites `D-1`) and are NOT
           graded here: they are an unreconciled second usage and grading them
           would invent a family rather than read one. Stated, not silent. A
           lettered sub-row (`D1a`) falls back to its base row (`D1`).
    C-nn   `docs/COST_CALIBRATION.md`, a table row `^| [**]C-nn[**] |` [27 rows].
    N-XXn  `docs/NUMERICS_KNOWLEDGE.md`, either a heading `^#{1,6} [**]N-XXn` or
           a bold lead `^**N-XXn.` -- BOTH forms are in use and both are read
           [92 ids across the N-B, N-D, N-K, N-T and N-X families].

  DANGLING is a DISTINCT VERDICT, never a silent skip: an id cited at the graded
  tree whose defining row does not exist at that tree. It is reported in its own
  block and is never a FIRE -- it is not a timing finding, it is a missing row,
  and the two must not be blended. At HEAD the DANGLING set is small and mostly
  real signal (`L-258` cited on the board before its lesson block was appended);
  it also carries a KNOWN FALSE-POSITIVE CLASS, disclosed rather than engineered
  away -- a certificate serial in `docs/DOCKET.md` reads as `C-2026`, and
  `D188`/`D901` are the two non-citations `D349` already documents as such.

  REFUSAL, limb 2: if a family's DEFINING FILE is absent from the graded tree
  while ids of that family are cited, every one of those ids would silently read
  DANGLING -- a mass skip wearing a verdict's clothes. That is a CANNOT-ADJUDICATE
  refusal, exit 2 (rule 3: a reader that cannot see must say so). The check is
  conditional on a citation existing, so a tree carrying neither is graded
  normally.

ATTRIBUTION, both limbs. The introducing commit is taken from
`git blame -w --line-porcelain` at the graded revision. Blame names the commit
that LAST TOUCHED the line, which for a reflowed or moved line can be later than
the commit that first wrote the stamp -- or the citation. That error is
conservative in the safe direction for limb 1: a later committer date makes the
delta smaller and the check quieter, so blame can hide a fire but cannot
manufacture one. For limb 2 the limitation is the same but cuts BOTH ways, and
that is stated rather than glossed: a reflowed CITING line reads later (quieter),
while a reflowed DEFINING row reads later (louder). A limb-2 fire is therefore
triaged by reading both commits, not believed on sight. `--at <sha>` grades a
committed tree, which is how a historical instance is reproduced.

KNOWN FALSE-POSITIVE CLASS, disclosed rather than engineered away: a genuinely
future-dated time written without a cue word (a progress-table ETA rendered as
`**~2026-08-23 01:40Z**`) reads as a FIRE. Triage the fire; do not widen the
cue list to make a red go away.

EXIT CODES.  0 report ran (or --strict with no fire).  1 --strict with >= 1 FIRE
from EITHER limb, or a selftest control failed.  2 REFUSAL: CANNOT-PARSE,
CANNOT-ADJUDICATE, a blame/ls-tree failure, or the shared skew model unavailable.
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


# -------------------------------------------------------------------- ids ---
# Limb 2. Token forms and defining-row forms are READ from the HEAD blobs (see
# the header) -- in particular the docket id carries no hyphen and the numerics
# ids appear under two heading forms, both of which are matched here.

ID_TOKEN_RES = (
    ("L", re.compile(r"\bL-(\d+)\b")),
    ("D", re.compile(r"\bD(\d{1,4}[a-z]?)\b")),
    ("C", re.compile(r"\bC-(\d+)\b")),
    ("N", re.compile(r"\bN-([A-Z]+\d+[a-z]?)\b")),
)

ID_DEFS = {
    "L": ("docs/LESSONS.md", re.compile(r"^#{1,6}\s+L-(\d+)\b")),
    "D": ("docs/DOCKET.md",
          re.compile(r"^\|\s*\*{0,2}D(\d+[a-z]?)\*{0,2}\s*\|")),
    "C": ("docs/COST_CALIBRATION.md",
          re.compile(r"^\|\s*\*{0,2}C-(\d+)\*{0,2}\s*\|")),
    "N": ("docs/NUMERICS_KNOWLEDGE.md",
          re.compile(r"^(?:#{1,6}\s+\*{0,2}|\*\*)N-([A-Z]+\d+[a-z]?)\b")),
}


class CannotAdjudicate(Exception):
    """A family's defining file is absent while ids of that family are cited.

    Every such id would read DANGLING, which is a mass skip wearing a verdict's
    clothes. Refused instead (rule 3).
    """


def id_definition_lines(repo, rev, families):
    """{(fam, ident): lineno} for every defining row of `families` present at rev.

    Raises CannotAdjudicate when a needed defining file is not in the tree.
    """
    out = {}
    for fam in sorted(families):
        path, rx = ID_DEFS[fam]
        try:
            lines = blob_lines(repo, rev, path)
        except RuntimeError as exc:
            raise CannotAdjudicate(
                "ids of family %r are cited at %s but its defining file %s is not "
                "in that tree (%s) -- REFUSING to report every one of them as "
                "DANGLING, which would be a mass skip wearing a verdict's clothes"
                % (fam, rev, path, str(exc)[:60]))
        for n, line in enumerate(lines, 1):
            m = rx.match(line)
            if m and (fam, m.group(1)) not in out:
                out[(fam, m.group(1))] = n
    return out


def _def_key(defs, fam, ident):
    """Defining row for this id, with the lettered-sub-row fallback (D1a -> D1)."""
    if (fam, ident) in defs:
        return (fam, ident)
    base = ident.rstrip("abcdefghijklmnopqrstuvwxyz")
    if base and (fam, base) in defs:
        return (fam, base)
    return None


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

def sweep(repo, rev="HEAD", paths=None, do_ids=True):
    """Returns (rows, counts) for BOTH limbs over one pass of the corpus.

    Raises CannotParse on a marked-but-invalid stamp token, CannotAdjudicate when
    a cited id family has no defining file at `rev`.
    """
    files = paths if paths else tree_files(repo, rev)
    rows = []
    counts = dict(files=0, tokens=0, graded=0, unmarked=0, planned=0, fires=0,
                  id_files=0, id_tokens=0, id_graded=0, id_dangling=0, id_fires=0)
    id_hits = []                      # (path, n, fam, ident, tok, sha, ctime)
    for path in sorted(files):
        lines = blob_lines(repo, rev, path)
        hits, ihits = [], []
        for n, line in enumerate(lines, 1):
            for tok, col, ts, kind in stamps_in(line):
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
            if not do_ids:
                continue
            for fam, rx in ID_TOKEN_RES:
                for m in rx.finditer(line):
                    counts["id_tokens"] += 1
                    ihits.append((n, fam, m.group(1), m.group(0)))
        if not hits and not ihits:
            continue
        if hits:
            counts["files"] += 1
        if ihits:
            counts["id_files"] += 1
        att = blame(repo, rev, path,
                    [h[0] for h in hits] + [h[0] for h in ihits])
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
        for n, fam, ident, tok in ihits:
            if n not in att:
                raise RuntimeError("blame returned no attribution for %s:%d" % (path, n))
            sha, ctime = att[n]
            id_hits.append((path, n, fam, ident, tok, sha, ctime))

    if not id_hits:
        return rows, counts

    # --- limb 2: the defining row of every id actually cited -----------------
    defs = id_definition_lines(repo, rev, {h[2] for h in id_hits})
    need = {}
    for h in id_hits:
        key = _def_key(defs, h[2], h[3])
        if key is not None:
            need.setdefault(ID_DEFS[key[0]][0], set()).add(defs[key])
    datt = {}
    for dpath, linenos in need.items():
        datt[dpath] = blame(repo, rev, dpath, sorted(linenos))

    for path, n, fam, ident, tok, sha, ctime in id_hits:
        key = _def_key(defs, fam, ident)
        if key is None:
            counts["id_dangling"] += 1
            rows.append(dict(path=path, line=n, tok=tok, kind="DANGLING",
                             fam=fam, ident=ident, sha=sha, ctime=ctime,
                             dsha=None, dctime=None, delta=None, dpath=None))
            continue
        dpath, dline = ID_DEFS[fam][0], defs[key]
        if dline not in datt.get(dpath, {}):
            raise RuntimeError("blame returned no attribution for the defining "
                               "row %s:%d (%s)" % (dpath, dline, tok))
        dsha, dctime = datt[dpath][dline]
        # SAME comparison, SAME tolerance as limb 1: is the DEFINITION ahead of
        # the CITATION? If so the id was cited before it existed.
        status, delta = stamp_skew.ahead_verdict(dctime, ctime)
        counts["id_graded"] += 1
        kind = "ID-FIRE" if status == "ahead" else "ok-id"
        if status == "ahead":
            counts["id_fires"] += 1
        rows.append(dict(path=path, line=n, tok=tok, kind=kind, fam=fam,
                         ident=ident, sha=sha, ctime=ctime, dsha=dsha,
                         dctime=dctime, delta=delta,
                         dpath="%s:%d" % (dpath, dline)))
    return rows, counts


def iso(epoch):
    return datetime.datetime.fromtimestamp(
        epoch, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def report(rows, counts, show_all=False, do_ids=True):
    fires = [r for r in rows if r["kind"] == "FIRE"]
    planned = [r for r in rows if r["kind"] == "PLANNED"]
    print("LIMB 1 -- stamps vs the commit that introduced their line")
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

    id_fires = [r for r in rows if r["kind"] == "ID-FIRE"]
    if do_ids:
        dangling = [r for r in rows if r["kind"] == "DANGLING"]
        print("\nLIMB 2 -- id citations vs the commit that appended their defining row")
        print("  scanned  %d corpus files carrying ids, %d id tokens "
              "(L-nnn, Dnnn, C-nn, N-XXn)"
              % (counts["id_files"], counts["id_tokens"]))
        print("  graded   %d citations against their defining row's introducing "
              "commit" % counts["id_graded"])
        print("  DANGLING %d citations whose defining row does not exist at this "
              "tree (distinct verdict, never a fire)" % counts["id_dangling"])
        print("  FIRES    %d" % counts["id_fires"])
        if id_fires:
            print("\n  %-46s %-8s %-10s %-10s %s"
                  % ("file:line", "id", "cite", "define", "cited AHEAD by"))
            ordered = sorted(id_fires, key=lambda r: -r["delta"])
            cap = len(ordered) if show_all else 40
            for r in ordered[:cap]:
                print("  %-46s %-8s %-10s %-10s %+d s (%+.1f h)  def %s"
                      % ("%s:%d" % (r["path"], r["line"]), r["tok"],
                         r["sha"][:8], r["dsha"][:8], r["delta"],
                         r["delta"] / 3600.0, r["dpath"]))
            if len(ordered) > cap:
                print("  ... %d further limb-2 fires not listed (--show-all "
                      "prints them all)" % (len(ordered) - cap))
        if dangling:
            seen, shown = set(), 0
            print("\n  DANGLING (reported separately, never silently skipped):")
            for r in sorted(dangling, key=lambda r: (r["fam"], r["ident"])):
                if r["tok"] in seen:
                    continue
                seen.add(r["tok"])
                n = sum(1 for x in dangling if x["tok"] == r["tok"])
                print("    %-10s %2d citation(s), first at %s:%d"
                      % (r["tok"], n, r["path"], r["line"]))
                shown += 1
                if shown >= 40:
                    print("    ... %d further distinct dangling ids not listed"
                          % (len({x["tok"] for x in dangling}) - shown))
                    break
    return fires, id_fires


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


def _mkrepo_ids(tmp):
    """Planted repo for limb 2: four commits, one hour apart, ids planted so that
    the citing/defining ORDER is known by construction rather than inferred.

      12:00Z  LAB_STATE cites L-900 (C7) and L-999 (C10); LESSONS defines L-1
      13:00Z  LESSONS defines L-900          -> C7 is a citation one commit early
      14:00Z  LESSONS defines L-901 AND LAB_STATE cites it in the SAME commit (C8)
      15:00Z  LAB_STATE cites L-900 again, two commits after it existed (C9)
    """
    os.makedirs(os.path.join(tmp, "docs"))
    state = os.path.join(tmp, "docs", "LAB_STATE.md")
    less = os.path.join(tmp, "docs", "LESSONS.md")

    def write(p, lines):
        with open(p, "w") as fh:
            fh.write("\n".join(lines) + "\n")

    def commit(hh, paths):
        stamp = "2026-08-24T%02d:00:00+00:00" % hh
        env = dict(os.environ, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp,
                   GIT_AUTHOR_NAME="control", GIT_AUTHOR_EMAIL="c@x",
                   GIT_COMMITTER_NAME="control", GIT_COMMITTER_EMAIL="c@x")
        for cmd in (["add"] + paths, ["commit", "-q", "-m", "control %d" % hh]):
            p = subprocess.run(["git", "-C", tmp] + cmd, env=env,
                               capture_output=True, text=True)
            if p.returncode != 0:
                raise RuntimeError("id control repo setup failed: %s" % p.stderr)

    p = subprocess.run(["git", "-C", tmp, "init", "-q", "-b", "main"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("id control repo init failed: %s" % p.stderr)

    state_lines = [
        "## verification",
        "C7 planted: cites L-900 one commit BEFORE its defining row exists",
        "C10 planted: cites L-999, a row that is never defined at all",
    ]
    less_lines = ["# lessons", "## L-1. the base lesson, defined at 12:00Z"]
    write(state, state_lines)
    write(less, less_lines)
    commit(12, ["docs/LAB_STATE.md", "docs/LESSONS.md"])

    less_lines.append("## L-900. planted definition, appended at 13:00Z")
    write(less, less_lines)
    commit(13, ["docs/LESSONS.md"])

    less_lines.append("## L-901. planted definition, appended at 14:00Z")
    state_lines.append("C8 planted: cites L-901 in the SAME commit as its row")
    write(less, less_lines)
    write(state, state_lines)
    commit(14, ["docs/LAB_STATE.md", "docs/LESSONS.md"])

    state_lines.append("C9 planted: cites L-900 two commits AFTER its row landed")
    write(state, state_lines)
    commit(15, ["docs/LAB_STATE.md"])
    return tmp


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

    # C7/C8/C9/C10 -- one planted repo, four commits, the ORDER known by
    # construction. C7 is limb 2's non-zero: a zero from this limb is worth
    # nothing unless the same reader has been shown seeing a fire (rule 3).
    tmp = tempfile.mkdtemp(prefix="idctl_")
    try:
        _mkrepo_ids(tmp)
        rows, counts = sweep(tmp, "HEAD")
        st = {r["line"]: r for r in rows
              if r["path"] == "docs/LAB_STATE.md" and r["kind"] != "UNMARKED"}
        rec("C7 id cited ONE COMMIT BEFORE its defining row MUST fire",
            st.get(2, {}).get("kind") == "ID-FIRE" and st[2]["delta"] == 3600,
            "line 2 (L-900) -> %s, cited %+d s early"
            % (st.get(2, {}).get("kind"), st.get(2, {}).get("delta", 0)))
        rec("C8 id cited in the SAME commit as its row must NOT fire",
            st.get(4, {}).get("kind") == "ok-id" and st[4]["delta"] == 0,
            "line 4 (L-901) -> %s, delta %+d s"
            % (st.get(4, {}).get("kind"), st.get(4, {}).get("delta", 0)))
        rec("C9 id cited AFTER its row landed must NOT fire",
            st.get(5, {}).get("kind") == "ok-id" and st[5]["delta"] == -7200,
            "line 5 (L-900) -> %s, delta %+d s"
            % (st.get(5, {}).get("kind"), st.get(5, {}).get("delta", 0)))
        rec("C10 id with NO defining row -> DANGLING, not a fire and not skipped",
            st.get(3, {}).get("kind") == "DANGLING"
            and counts["id_dangling"] == 1 and counts["id_fires"] == 1,
            "line 3 (L-999) -> %s; dangling %d, id fires %d"
            % (st.get(3, {}).get("kind"), counts["id_dangling"],
               counts["id_fires"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # C11 -- the defining FILE is missing while its ids are cited: every one of
    # them would read DANGLING, which is a mass skip wearing a verdict's clothes
    tmp = tempfile.mkdtemp(prefix="idctl_")
    try:
        _mkrepo(tmp, ["## verification",
                      "C11 planted: cites L-900 in a tree with no LESSONS.md"],
                CONTROL_BASE)
        try:
            sweep(tmp, "HEAD")
            rec("C11 cited family with no defining file -> CANNOT-ADJUDICATE",
                False, "sweep returned instead of refusing")
        except CannotAdjudicate as exc:
            rec("C11 cited family with no defining file -> CANNOT-ADJUDICATE",
                True, str(exc)[:70])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # C5 -- the known real instance, reproduced from the tree that carried it.
    # Limb 1 only: C5 is the stamp limb's real-world control and is left exactly
    # as it was, so the new limb cannot change what it proves.
    C5_SHA = "82194ec5"
    try:
        rows, counts = sweep(repo, C5_SHA, paths=["docs/LAB_STATE.md"],
                             do_ids=False)
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
            # Limb 2's comparison. Argument ORDER is the whole semantics here:
            # (defining, citing) asks "was the id cited before its row existed?",
            # and the swap asks the opposite question while still returning a
            # verdict, which is exactly the failure a selftest must catch.
            # Anchored by its own newline and indent for the same reason the
            # tolerance mutant is: the bare call text also occurs in THIS list.
            ("limb-2 comparison direction swapped", "check_stamp_vs_commit.py",
             "\n        status, delta = stamp_skew.ahead_verdict(dctime, ctime)\n",
             "\n        status, delta = stamp_skew.ahead_verdict(ctime, dctime)\n"),
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
    # GRANULARITY, stated so the number is unambiguous. The record has carried
    # two different counts of the same thing ("nine planted controls" in
    # docs/COST_CALIBRATION.md C-25, "six" on the verification board): both were
    # true of different granularities. This line names all three.
    mut = [r for r in results if r[0].startswith("C6 mutant")]
    named = [r for r in results if not r[0].startswith("C6 mutant")]
    print("\n  %d named controls, %d mutants, %d results; %d failed"
          % (len(named), len(mut), len(results), len(bad)))
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
    ap.add_argument("--selftest", action="store_true",
                    help="run planted controls C1-C11 plus the C6 mutation harness")
    ap.add_argument("--no-ids", action="store_true",
                    help="limb 1 only: do not grade id citations against their "
                         "defining rows")
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
    do_ids = not args.no_ids
    try:
        rows, counts = sweep(repo, args.at, paths=args.path, do_ids=do_ids)
    except CannotParse as exc:
        sys.stderr.write("REFUSAL (CANNOT-PARSE): %s\n" % exc)
        return 2
    except CannotAdjudicate as exc:
        sys.stderr.write("REFUSAL (CANNOT-ADJUDICATE): %s\n" % exc)
        return 2
    except RuntimeError as exc:
        sys.stderr.write("REFUSAL: %s\n" % exc)
        return 2
    fires, id_fires = report(rows, counts, show_all=args.show_all, do_ids=do_ids)
    print("\n" + "-" * 70)
    if fires:
        print("%d stamp(s) written AHEAD of the commit that introduced them "
              "(bd3edfe8 defect class)." % len(fires))
        print("Triage each: a stamp is written only from a `date -u` read in the "
              "SAME shell invocation as the write.")
    else:
        print("No stamp in the corpus leads its introducing commit by more than "
              "%d s." % FORWARD_TOLERANCE_S)
    if do_ids:
        if id_fires:
            print("%d id citation(s) written AHEAD of the commit that appended "
                  "the cited row (D488/C-15 instance class)." % len(id_fires))
            print("Triage each: an id is re-derived from the TAIL at commit "
                  "(rule 11), never guessed from a count beforehand.")
        else:
            print("No id citation in the corpus precedes its own defining row by "
                  "more than %d s." % FORWARD_TOLERANCE_S)
    print("NOTE: blame attributes a line to its LAST toucher. For limb 1 that can "
          "hide a fire but cannot manufacture one; for limb 2 it cuts both ways "
          "(a reflowed citation reads quieter, a reflowed defining row louder), "
          "so read both commits before believing a limb-2 fire.")
    return 1 if ((fires or id_fires) and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
