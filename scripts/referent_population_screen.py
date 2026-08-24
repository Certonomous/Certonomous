#!/usr/bin/env python3
r"""Re-derivable population screen for docs/EXTERNAL_REFERENT_AUDIT.md.

WHY THIS FILE EXISTS
====================
The audit ran two instruments and committed neither. §11.1 states the
consequence against itself: §3's bucket figures "cannot be re-derived by
anyone, now or later". §11's own population figures inherited the same defect
-- commit e3f3b521 touched one file, the audit prose, and no producer. This is
that producer, committed.

SCOPE, STATED SO IT CANNOT BE OVERREAD
======================================
This implements §2's POPULATION rule only. It does NOT reconstruct §3's
EXTERNAL / SELF-REFERENTIAL / BOTH / UNDECLARED buckets. Those two vocabulary
lists are not in the repository in any commit, and §11.5 item 2 rules that
rebuilding them from the prose "would be a different instrument reporting
under this document's numbers". So §3's 408 / 83 / 93 / 965 stay
unreproducible, and this script does not pretend otherwise.

WHAT IT IMPLEMENTS -- the rule as §2 writes it
==============================================
  frame  git ls-tree at a NAMED REVISION, '*.md' -- blobs, never the worktree,
         so the same command returns the same numbers at any later date.
  unit   the markdown section, heading-delimited (^#{1,6}\s).
  rule   a section qualifies as a verification if it carries a verification
         VERB, or a fixed verdict TOKEN together with a number.

§2 does not state case-sensitivity, and §11.1 measured that this one unstated
choice moves the answer by 35%. Both readings are therefore reported side by
side and NEITHER is privileged:

  strict  token as a case-SENSITIVE substring    (§11.1's 1,008 reading)
  ci_wb   token case-INSENSITIVE, word-bounded   (§11.1's 1,567 reading -- the
          frame §11.2's population table declares it used)

Also counted: D-B6-8's metric, markdown tables whose HEADER row carries a
`reference` column.

PLANTED CONTROL (constitution rule 3)
=====================================
Before any population number is taken, seven known sections are written to a
file ON DISK, hashed into the object database, and read back THROUGH THE SAME
git blob reader and THE SAME predicates that produce the population figures.
The plants are chosen to fail in both directions:

  1 verb only .................. qualifies under both readings
  2 TOKEN + number ............. qualifies under both readings
  3 lowercase token + number ... qualifies under ci_wb, NOT under strict
  4 number, no token, no verb .. qualifies under NEITHER
  5 TOKEN, no number ........... qualifies under NEITHER
  6 table, `reference` header .. counted by the reference-column metric
  7 table, `reference` in body . NOT counted by it

Plant 3 is the one that matters most: a screen whose two readings were silently
the same code path would classify it identically and be caught here. Plants 4
and 5 pin the two halves of the token-AND-number conjunction. Plant 7 is
checked by WHICH header row matched, not by the count, because a header/body
confusion preserves the count. Mutation-tested 2026-08-24: inverting the
case-insensitivity, the heading regex, the digit requirement and the
header/body offset are each caught. The script REFUSES -- exit 2, no numbers
printed -- if any plant does not read back in its known bucket.

The control writes one unreferenced loose blob per run (`git hash-object -w`).
It touches no ref and no index; git gc reclaims it.

Usage:  scripts/referent_population_screen.py [REV ...]      (default: HEAD)
"""
import json
import os
import re
import subprocess
import sys
import tempfile

def repo_root():
    """Ask git, not __file__ -- so a copy of this script run from anywhere
    inside the tree screens the same repository it is checked into."""
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("REFUSED: not inside a git repository\n")
        raise SystemExit(2)
    return r.stdout.strip()


REPO = repo_root()

# Quoted verbatim from docs/EXTERNAL_REFERENT_AUDIT.md §2 ("Population rule").
TOKENS = ["PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
          "VALIDATED", "SOLVER-BACKED", "RESEARCH MODEL", "UNCONVERGED"]
VERBS = ["verified against", "confirmed by", "validated against", "cross-checked",
         "checked against", "reproduces", "graded against", "compared against",
         "re-measured"]

HEADING = re.compile(r"^#{1,6}\s")
DIGIT = re.compile(r"\d")
TOKEN_CI_WB = re.compile(r"\b(" + "|".join(re.escape(t) for t in TOKENS) + r")\b",
                         re.IGNORECASE)
READINGS = ("strict", "ci_wb")


def split_sections(text):
    """The audit's unit: heading-delimited blocks, preamble included."""
    cur, out = [], []
    for line in text.splitlines():
        if HEADING.match(line):
            if cur:
                out.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return out


def qualifies(section, reading):
    """§2's rule. `reading` fixes the one thing §2 leaves unstated."""
    if any(v in section.lower() for v in VERBS):
        return True
    if not DIGIT.search(section):
        return False
    if reading == "strict":
        return any(t in section for t in TOKENS)
    if reading == "ci_wb":
        return bool(TOKEN_CI_WB.search(section))
    raise ValueError("unknown reading: %r" % reading)


def is_table_separator(line):
    s = line.strip()
    return s.startswith("|") and "-" in s and set(s) <= set("|-: ")


def reference_header_tables(text):
    """D-B6-8's metric: tables whose HEADER row carries a `reference` column.

    The header is the line above the |---| separator; a `reference` in a BODY
    cell does not count. Returns the matching HEADER LINES, not a count: a
    header/body confusion can preserve the count while matching the wrong row,
    and the control can only catch that if it can see WHICH row matched.
    """
    lines = text.splitlines()
    hits = []
    for i in range(1, len(lines)):
        if not is_table_separator(lines[i]):
            continue
        header = lines[i - 1]
        if "|" not in header:
            continue
        if any("reference" in c.lower() for c in header.split("|")):
            hits.append(header)
    return hits


def read_blobs(specs):
    """One `git cat-file --batch` for the whole corpus. Refuses on any spec git
    cannot resolve -- a silently-skipped file is a silently-wrong count."""
    with tempfile.NamedTemporaryFile("w", suffix=".specs", delete=False) as fh:
        fh.write("\n".join(specs) + "\n")
        spec_file = fh.name
    try:
        with open(spec_file) as stdin:
            raw = subprocess.run(["git", "cat-file", "--batch"], stdin=stdin,
                                 cwd=REPO, stdout=subprocess.PIPE,
                                 check=True).stdout
    finally:
        os.unlink(spec_file)
    pos, out = 0, []
    for spec in specs:
        eol = raw.index(b"\n", pos)
        head = raw[pos:eol].decode().split()
        if len(head) != 3 or head[1] != "blob":
            die("git cat-file could not resolve %s: %s" % (spec, " ".join(head)))
        size = int(head[2])
        body = raw[eol + 1:eol + 1 + size]
        pos = eol + 1 + size + 1
        out.append((spec, body.decode("utf-8", "replace")))
    return out


def md_paths(rev):
    listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev],
                             cwd=REPO, capture_output=True, text=True,
                             check=True).stdout.splitlines()
    return sorted(p for p in listing if p.endswith(".md"))


def screen(rev):
    paths = md_paths(rev)
    blobs = read_blobs(["%s:%s" % (rev, p) for p in paths])
    totals = {"revision": rev, "tracked_md": len(paths), "sections_total": 0,
              "verification_sections": {}, "docs_carrying_one": {},
              "reference_header_tables": 0, "docs_with_reference_header": 0}
    for r in READINGS:
        totals["verification_sections"][r] = 0
        totals["docs_carrying_one"][r] = 0
    for _spec, text in blobs:
        secs = split_sections(text)
        totals["sections_total"] += len(secs)
        for r in READINGS:
            n = sum(1 for s in secs if qualifies(s, r))
            totals["verification_sections"][r] += n
            if n:
                totals["docs_carrying_one"][r] += 1
        t = len(reference_header_tables(text))
        totals["reference_header_tables"] += t
        if t:
            totals["docs_with_reference_header"] += 1
    if totals["sections_total"] == 0:
        die("zero sections over %d files at %s -- reader is blind" %
            (len(paths), rev))
    return totals


PLANT_TEXT = """## plant one: verb only
The inlet premise was verified against the benchmark's own file.

## plant two: token and number
Verdict: GATE FAIL at 3 of 9 rows.

## plant three: lowercase token and number
Verdict: gate fail on 3 of 9 rows.

## plant four: number, no token, no verb
Prose carrying the numeral 3 and nothing else of interest.

## plant five: token but no number anywhere
Verdict: GATE FAIL, and not a numeral in this section.

## plant six: table carrying a reference column in its header
| case | reference | value |
| --- | --- | --- |
| a | Roshko 1954 | 0.212 |

## plant seven: table carrying reference only in a body cell
| case | source | value |
| --- | --- | --- |
| a | a reference lives in this body cell | 0.212 |

This closing sentence exists so that no planted table row is the last line of
the plant, where a header/body offset error could never be reached.
"""

PLANT_HEADER = "| case | reference | value |"   # plant six's header row

# (section index, reading, expected verdict). Each line is a way the screen
# could be wrong; together they pin every branch of `qualifies`.
PLANT_EXPECT = [(0, "strict", True), (0, "ci_wb", True),     # verb wins alone
                (1, "strict", True), (1, "ci_wb", True),     # token + number
                (2, "strict", False), (2, "ci_wb", True),    # the two readings
                (3, "strict", False), (3, "ci_wb", False),   # number alone
                (4, "strict", False), (4, "ci_wb", False),   # token alone
                (5, "strict", False), (5, "ci_wb", False),   # a table is not one
                (6, "strict", False), (6, "ci_wb", False)]


def die(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    raise SystemExit(2)


def planted_control():
    """Write the plants to disk, read them back through the production reader,
    classify with the production predicates, refuse on any disagreement."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(PLANT_TEXT)
        path = fh.name
    try:
        sha = subprocess.run(["git", "hash-object", "-w", path], cwd=REPO,
                             capture_output=True, text=True,
                             check=True).stdout.strip()
        (_spec, back), = read_blobs([sha])
    finally:
        os.unlink(path)
    if back != PLANT_TEXT:
        die("plant did not survive the blob round trip")
    secs = split_sections(back)
    if len(secs) != 7:
        die("plant split into %d sections, expected 7 -- splitter is wrong"
            % len(secs))
    for idx, reading, expected in PLANT_EXPECT:
        got = qualifies(secs[idx], reading)
        if got != expected:
            die("plant %d under reading %s classified %s, expected %s"
                % (idx + 1, reading, got, expected))
    hits = reference_header_tables(back)
    if hits != [PLANT_HEADER]:
        die("reference-column metric matched %r; expected exactly plant six's "
            "header row (plant seven's body cell must not count)" % (hits,))
    return {"plant_blob": sha, "sections": len(secs),
            "checks": len(PLANT_EXPECT) + 3, "verdict": "PLANT READ BACK"}


def main(argv):
    control = planted_control()
    revs = argv[1:] or ["HEAD"]
    result = {"planted_control": control,
              "revisions": [screen(r) for r in revs]}
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
