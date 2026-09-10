#!/usr/bin/env python3
"""Commit-SUBJECT screen. Reads history; it never writes, never commits, never gates.

WHY THIS EXISTS
---------------
`docs/LESSONS.md` L-524 (commit 5565987a) and L-524 ADDENDUM A (b81b00e0): the
commit MESSAGE is the one artifact the private-index protocol never checks. Two
lanes sharing a per-ROLE scratch directory with generic message filenames
(`msg1`, `msg2`) raced, and `git commit-tree -F msg2` committed a message its
lane never wrote. SEVEN such commits are on main permanently -- 878f1556,
3dc99590, 28b05eb2, 4d9d902b, b95d6d2c, 3def5d39, badbcfd2 -- and every one of
them passed `git diff-tree --stat`, the CAS on `update-ref`, and the
post-commit `git diff HEAD~1 HEAD --stat`. All three of those instruments read
the TREE. None of them reads the SUBJECT. This file asks the one question none
of them asked.

The sharpest instance, 3def5d39: a tree touching only `verification/runs/
T-family/T11_runs/...` plus `docs/COST_CALIBRATION.md`, carrying the subject
"T4 GRADE RECORD [lab-attributed]: NOT A RESULT x3" -- a grade verdict filed
under a rung it did not grade.

WHAT THIS IS NOT, STATED FIRST BECAUSE IT IS THE POINT
------------------------------------------------------
It is ADVISORY and it is the only state any agent may put it in. Docket D539
(2026-08-27, verification): "A checker that refuses a commit is a GATE ON LAB
PROCESS, and ADDING a gate is reserved to Sanaa exactly as retiring one is ...
NO AGENT MAY FLIP IT. Not cfd, not this team, not the chief. A measured rate
that 'looks acceptable' is not an authorisation." Accordingly:

  * A sweep that finds a hundred suspect commits still exits 0. Findings are
    REPORTED on stdout. There is no flag, no environment variable and no
    argument in this file that can make a finding non-zero, because the flag
    would be the gate.
  * Exit 2 NEVER means "a commit is bad". It means the INSTRUMENT could not
    run (a git failure, an unparseable log record, a failed selftest). That
    distinction is the whole exit-code contract.
  * It never rewrites history, never touches the index, never calls a writing
    git subcommand, never reads the working tree for repository DATA, never
    checks anything out, and it starts no network and no compute.

It also never repairs. None of the seven is correctable -- main is not
rewritten -- so the product of this screen is DISCLOSURE, which is exactly what
L-524 ADDENDUM A said the repair is.

EXIT CODES
    0   the screen ran (findings, if any, are on stdout) -- ADVISORY, D539
    1   usage error
    2   the instrument could not run, or --selftest failed

`python3 -O` PARITY, AND A DELIBERATE DIVERGENCE FROM check_commit_size.py
--------------------------------------------------------------------------
L-332: `python3 -O` deletes `assert` statements, so a selftest built out of
bare asserts passes VACUOUSLY under -O. `scripts/check_commit_size.py` answers
that by REFUSING to run under -O at all (its module-level `if not __debug__`
bail, and D539 records rc 2 under `-O --selftest` as a verified control).

This file takes the other, stricter road and must be read as a divergence, not
an oversight: it contains ZERO `assert` statements -- every control is an
explicit `if` that raises or records a failure -- and `--selftest` parses this
file's own AST and REFUSES if a single `ast.Assert` node exists. The screen is
therefore required to behave IDENTICALLY under `python3` and `python3 -O`:
same control count, same exit code. If the two ever differ, that is a defect in
this selftest, not a curiosity, and the operator is told to treat it as one.
The divergence is deliberate because a "refuse under -O" guard proves only that
the guard noticed the flag; a zero-assert guard proves the checks are still
there when the flag is set.

WHAT IT MEASURES -- TWO DETECTORS
---------------------------------
(i) DUP: DUPLICATE SUBJECT ON DISJOINT TREES.
    Two commits within a window of W commits carry the same NORMALIZED subject
    and their changed-path sets do not intersect. This is L-524's own published
    detection rule.

    NORMALIZATION, STATED IN FULL AND KEPT AS SMALL AS IT CAN BE DEFENDED --
    every normalization step invents false positives, so each one below has to
    earn its place:
        * leading and trailing whitespace stripped;
        * each internal run of whitespace collapsed to one space.
    AND NOTHING ELSE. Specifically NOT done, with the reason:
        * NO case folding. Subjects here are frequently shouted; folding would
          merge "T4 GRADE RECORD" with a genuinely different lower-case subject
          and would also make the id vocabulary lossy, since rung ids carry
          meaningful lowercase (K0c, T1b, T23G2Rn2).
        * NO stripping of a trailing marker such as "[lab-attributed]" -- that
          marker distinguishes two real and different claims.
        * NO stripping of the leading team prefix ("dafoam: ", "closure ") --
          two teams writing the same headline is a coincidence worth seeing,
          and stripping it would manufacture pairs.
        * NO punctuation or unicode normalization.
    A race copies a message BYTE FOR BYTE, so exact equality would already
    find every instance of the class this screen is built for; the whitespace
    clause exists only so that a subject re-fed from a wrapped source is not
    silently missed.

    WINDOW W, DEFAULT 50 COMMITS, AND WHY. Measured on this repository's full
    history (7,507 commits on main at the time of writing): the seven known
    landed instances sit at commit-distances 1, 1, 2, 4, 6, 36 and 1 from
    their partner. The largest, b95d6d2c/ae9314c6, is 36 apart (19 minutes of
    wall clock with the fleet at full width). 50 is the next round number
    above the largest OBSERVED true separation, i.e. the measurement sets the
    default and not the other way round. The window is in COMMITS, not
    seconds, deliberately: commit distance is what the race is a function of
    (how many other lanes committed in between), it is deterministic, and it
    does not depend on a clock the box has already been caught misreading.
    Widening W is cheap in correctness and costly only in noise, because
    DISJOINTNESS, not proximity, does the discriminating work: --window 0
    means "no limit" and is supported so an auditor can price that himself.

(ii) MM: SUBJECT/TREE TOPIC MISMATCH.
    The subject names a rung or case identifier, the tree names at least one
    identifier of its own, and the two sets are DISJOINT. 3def5d39 is the
    archetype: subject {T4}, tree {T11}.

    THE ID VOCABULARY IS DERIVED FROM THE REPOSITORY, NEVER INVENTED. It is
    the set of DIRECTORY components under `cases/`, `verification/runs/` and
    `docs/campaigns/` in the scanned tree, tokenized (below) and filtered to
    tokens that look like an identifier. Directory components only, because a
    rung in this lab OWNS a directory; taking every basename as well would
    admit "MD5" (from *_MD5.txt) and "T0" (from B1_T0.txt) into the
    vocabulary. Paths of the SCANNED COMMITS are then folded in as a second
    source under the same rule, so an identifier that existed when the commit
    landed and has since been deleted is still known. The two sources are
    counted separately in the report.

    TWO ASYMMETRIES ON THE TREE SIDE, BOTH ONE-WAY. Basenames count as tree
    evidence though they do not create vocabulary, and tree matching is
    case-INSENSITIVE though subject matching is not (measured: 5a8f80e6 names
    L3 and its tree spells it autograde_t23g2r_l3.sh). Both widenings can only
    make a commit look MORE on-topic, i.e. they only ever REMOVE findings.

    ONE MEASURED FALSE-POSITIVE CLASS IS SEPARATED, NOT SUPPRESSED:
    MM-VARIANT-ID, where the subject names the PARENT rung of a variant the
    tree touches ("M1-C" over an M1c tree -- five of the seven mismatch flags
    in the last 500 commits). The relation is read off the lab's own naming
    convention (a variant extends the id with a LETTER) and is DIGIT-GUARDED:
    T1 over a T11 tree stays a finding, because T1 and T11 are different rungs
    and that is the exact shape the screen exists to catch. --variant-strict
    turns the class back into findings, so the exclusion is auditable from
    both sides.

    A SUBJECT NAMING NO IDENTIFIER IS NOT A FINDING. It is OUT OF POPULATION
    and is reported as its own counted class, distinctly from the clean ones.
    So is a commit whose TREE names no identifier -- a records-only commit to
    docs/LESSONS.md or docs/DOCKET.md legitimately discusses a rung it does
    not touch, and calling that a mismatch would drown the screen. Note what
    this costs: three of the seven known instances touch
    docs/COST_CALIBRATION.md, so "touches a records file" could NOT be used
    as an exclusion; only "touches NOTHING BUT records files" is.

FALSE-POSITIVE CLASSES ARE NAMED AND COUNTED, NEVER SILENTLY DROPPED
--------------------------------------------------------------------
Every commit the screen declines to flag lands in exactly one named class and
every class is printed with its count and, on --verbose, its members. A screen
that hides its exclusions cannot be audited, and the exclusions are where a
screen like this goes wrong.

TOKENIZATION (one rule, used on both the subject and the path side)
-------------------------------------------------------------------
A path component or subject word is cut at every character outside
[A-Za-z0-9-]; each remaining run is expanded into the run itself plus every
CONTIGUOUS hyphen-joined subsequence of it, and separately split on "_" and
"." first. So "D7-DEF-4" yields D7, DEF, 4, D7-DEF, DEF-4, D7-DEF-4 (and D7 is
in the vocabulary), while "VMFL063-R3" survives whole. Only tokens present in
the derived vocabulary are kept, on EITHER side, so the expansion cannot
invent an identifier.

ONE MEASURED PARSING HAZARD, RECORDED HERE BECAUSE IT COST AN HOUR
-------------------------------------------------------------------
`str.splitlines()` in Python splits on \x1c, \x1d and \x1e as well as \n. A
first draft used \x1e as a git --format field separator and `splitlines()` to
cut records; it silently produced twice as many rows as there were commits and
reported all seven known commits as "not in range". This file separates
RECORDS with NUL (`git log -z`) and FIELDS with \x1f, and never calls
splitlines() on git output.

USAGE
    python3 scripts/check_commit_subjects.py                      # last 500 on main
    python3 scripts/check_commit_subjects.py --rev main --count 500
    python3 scripts/check_commit_subjects.py --range 5565987a..HEAD
    python3 scripts/check_commit_subjects.py --all-history --verbose
    python3 scripts/check_commit_subjects.py --selftest
    python3 -O scripts/check_commit_subjects.py --selftest        # must match
"""
import sys
import ast
import json
import argparse
import subprocess
from pathlib import Path
from typing import NamedTuple

REPO_DEFAULT = Path(__file__).resolve().parent.parent

# The window default is a MEASUREMENT (see the module docstring), not a taste.
DEFAULT_WINDOW = 50
DEFAULT_COUNT = 500

# Borrowed, not invented: docs/standards/COMMIT_SIZE_GUARD.md fixes 50 files as
# the size at which a commit stops being one item, and scripts/check_commit_size.py
# encodes it as COUNT_MAX. A commit above it is a sweep, and a sweep's subject
# cannot be expected to name every tree it touches.
BULK_PATHS = 50

# Prefixes whose DIRECTORY components define the identifier vocabulary.
VOCAB_PREFIXES = ("cases", "verification/runs", "docs/campaigns")

# Only these git subcommands are ever spawned. Enforced at the single call site.
GIT_READ_ONLY = frozenset({"log", "ls-tree", "rev-parse"})

UPLOAD_SUBJECT = "Add files via upload"

# Every class the screen can put a commit in. Declared, so the report can print
# a class that fired ZERO times. A class that vanishes when empty lets a reader
# believe it was never applicable; "excluded 0 as bulk" is evidence, absence is
# not (this is the planted-zero principle applied to the report itself).
CLASS_NAMES = (
    "DUP-OUT-OF-WINDOW",
    "DUP-SERIES",
    "DUP-MERGE",
    "DUP-EMPTY",
    "DUP-UPLOAD",
    "DUP-BULK",
    "DUP-OVERLAP",
    "MM-MERGE",
    "MM-EMPTY",
    "MM-UPLOAD",
    "MM-BULK",
    "MM-NO-SUBJECT-ID (out of population)",
    "MM-NO-TREE-ID (out of population, records-only tree)",
    "MM-VARIANT-ID (subject names the parent rung of a tree variant)",
    "MM-MATCH (clean)",
)

REC = "\x01"   # record marker inside --format
FLD = "\x1f"   # field separator inside --format


class Refusal(Exception):
    """The instrument cannot run. NOT a verdict about any commit."""


class Commit(NamedTuple):
    sha: str
    n_parents: int
    ctime: int
    subject: str
    paths: tuple


# ---------------------------------------------------------------------------
# git, read-only, one process for the whole log
# ---------------------------------------------------------------------------

def git(args, repo):
    if not args or args[0] not in GIT_READ_ONLY:
        raise Refusal("git subcommand %r is not in the read-only allowlist %s"
                      % (args[:1], sorted(GIT_READ_ONLY)))
    proc = subprocess.run(["git"] + list(args), cwd=str(repo),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise Refusal("git %s failed rc=%d: %s"
                      % (" ".join(args), proc.returncode, proc.stderr.strip()[:400]))
    return proc.stdout


def parse_log(raw):
    """Parse `git log -z --name-only --format=REC%H FLD %P FLD %ct FLD %s`.

    Refuses on any record it cannot account for. A parser that skips what it
    does not understand reports a clean history it never read.
    """
    commits = []
    chunks = raw.split(REC)
    if chunks and chunks[0].strip("\x00\n") == "":
        chunks = chunks[1:]
    for chunk in chunks:
        parts = chunk.split("\x00")
        head = parts[0]
        fields = head.split(FLD)
        if len(fields) != 4:
            raise Refusal("log record has %d fields, expected 4: %r"
                          % (len(fields), head[:120]))
        sha, parents, ctime, subject = fields
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise Refusal("log record does not start with a 40-hex sha: %r" % sha[:80])
        if not ctime.isdigit():
            raise Refusal("log record commit time is not an integer: %r" % ctime[:40])
        paths = []
        for p in parts[1:]:
            p = p.lstrip("\n")
            if p:
                paths.append(p)
        commits.append(Commit(sha=sha,
                              n_parents=len(parents.split()) if parents.strip() else 0,
                              ctime=int(ctime),
                              subject=subject,
                              paths=tuple(paths)))
    return commits


def read_log(repo, rev, count, rng):
    args = ["log", "-z", "--name-only",
            "--format=%s%%H%s%%P%s%%ct%s%%s" % (REC, FLD, FLD, FLD)]
    if rng:
        args.append(rng)
    else:
        if count:
            args += ["-n", str(int(count))]
        args.append(rev)
    return parse_log(git(args, repo))


# ---------------------------------------------------------------------------
# normalization and tokenization -- the two places a screen invents its own
# false positives, so both are small and both are selftested
# ---------------------------------------------------------------------------

def normalize_subject(subject):
    """Strip the ends, collapse internal whitespace runs. Nothing else.

    No case folding, no marker stripping, no prefix stripping -- see the
    module docstring for why each of those is refused.
    """
    return " ".join(subject.split())


def _hyphen_expand(run):
    """"D7-DEF-4" -> the run, every hyphen piece, every contiguous join."""
    out = {run}
    pieces = [p for p in run.split("-") if p]
    for i in range(len(pieces)):
        for j in range(i, len(pieces)):
            out.add("-".join(pieces[i:j + 1]))
    return out


def _runs(text):
    """Maximal runs of [A-Za-z0-9-], then split each on '_' and '.'."""
    out = []
    cur = []
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch == "-"):
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def tokens(text):
    """Every candidate identifier token in a string. Membership filters later."""
    out = set()
    for run in _runs(text):
        for piece in run.replace("_", " ").replace(".", " ").split() + [run]:
            out |= _hyphen_expand(piece)
    return {t for t in out if t}


def looks_like_id(tok):
    """An identifier: starts upper, holds a digit, alnum/hyphen only, len>=2.

    Deliberately permissive on shape and strict on MEMBERSHIP -- the shape test
    only decides what may enter the vocabulary; nothing is treated as an id
    unless the repository itself named a directory that way.
    """
    if len(tok) < 2:
        return False
    if not (tok[0].isascii() and tok[0].isupper()):
        return False
    if tok[0] == "-" or tok[-1] == "-":
        return False
    if not any(c.isdigit() for c in tok):
        return False
    return all(c.isascii() and (c.isalnum() or c == "-") for c in tok)


def vocab_from_paths(paths, prefixes=None):
    """Identifier vocabulary from DIRECTORY components of paths.

    The final component of a path is its basename and is NOT a source -- see
    the module docstring (MD5, T0).
    """
    out = set()
    for p in paths:
        if prefixes is not None and not any(p == pre or p.startswith(pre + "/")
                                            for pre in prefixes):
            continue
        comps = p.split("/")[:-1]
        for comp in comps:
            for tok in tokens(comp):
                if looks_like_id(tok):
                    out.add(tok)
    return out


def ids_in(text, vocab):
    """Identifiers a string names, case-SENSITIVELY, restricted to the vocabulary."""
    return {t for t in tokens(text) if t in vocab}


def ci_index(vocab):
    """casefold -> {canonical tokens}. Collisions are kept, never resolved."""
    out = {}
    for t in vocab:
        out.setdefault(t.casefold(), set()).add(t)
    return out


def tree_ids(paths, vocab_ci):
    """Identifiers a commit's changed paths name. TWO deliberate asymmetries.

    (a) BASENAMES COUNT HERE, though they may not create vocabulary --
        K0cG_RESULTS.md is a K0cG artifact.
    (b) MATCHING IS CASE-INSENSITIVE HERE, though the subject side is
        case-sensitive. Measured cause: 5a8f80e6's subject names L3 and its
        tree is verification/runs/T-family/T23G2R_runs/autograde_t23g2r_l3.sh
        -- the file spells the rung in lower case, as scripts here do.

    Both asymmetries widen only the TREE side, i.e. they can only make a
    commit look MORE on-topic and therefore only ever REMOVE a finding. A
    screen may widen in the direction that costs it findings; widening the
    other way manufactures them.
    """
    out = set()
    for p in paths:
        for comp in p.split("/"):
            for t in tokens(comp):
                out |= vocab_ci.get(t.casefold(), set())
    return out


def is_variant_of(parent, child):
    """True if `child` is a lab-convention refinement of rung `parent`.

    The convention is read off the repository's own directory names: a rung's
    variants extend the id with a LETTER (M1 -> M1c, K0 -> K0c, T25R -> T25RF,
    D6RF -> D6RFn). The guard is the first extension character: if it is a
    DIGIT, the two ids are DIFFERENT RUNGS, not a rung and its variant --
    T1 and T11 are different rungs, and treating them as related would hide
    exactly the T4/T11 shape this screen exists to catch.
    """
    if not child.startswith(parent) or len(child) <= len(parent):
        return False
    return not child[len(parent)].isdigit()


# ---------------------------------------------------------------------------
# the screen
# ---------------------------------------------------------------------------

class Screen:
    """Both detectors over an already-read list of Commit records.

    Takes commits and a vocabulary as data, never git -- which is what lets
    --selftest drive it with planted failures and no repository at all.
    """

    def __init__(self, commits, vocab, window=DEFAULT_WINDOW, bulk=BULK_PATHS,
                 variant_strict=False):
        self.commits = list(commits)
        self.vocab = set(vocab)
        self.vocab_ci = ci_index(self.vocab)
        self.window = window
        self.bulk = bulk
        self.variant_strict = variant_strict
        self.dup_findings = []
        self.mm_findings = []
        self.classes = {}

    def _cls(self, name, item):
        self.classes.setdefault(name, []).append(item)

    # -- detector (i) -------------------------------------------------------
    def run_dup(self):
        by_subject = {}
        for i, c in enumerate(self.commits):
            by_subject.setdefault(normalize_subject(c.subject), []).append(i)

        for subject, idxs in sorted(by_subject.items()):
            if len(idxs) < 2:
                continue
            in_window = []
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    i, j = idxs[a], idxs[b]
                    if self.window and (j - i) > self.window:
                        self._cls("DUP-OUT-OF-WINDOW",
                                  "%s/%s dist=%d :: %s" % (self.commits[i].sha[:8],
                                                           self.commits[j].sha[:8],
                                                           j - i, subject[:70]))
                        continue
                    in_window.append((i, j))
            if len(in_window) >= 3:
                # Three or more co-occurrences inside one window is an addenda
                # or board series, not a two-lane race. Named and listed, never
                # dropped in silence.
                self._cls("DUP-SERIES",
                          "%dx :: %s :: %s" % (len(idxs), subject[:70],
                                               ",".join(self.commits[i].sha[:8]
                                                        for i in idxs)))
                continue
            for i, j in in_window:
                ci, cj = self.commits[i], self.commits[j]
                tag = "%s/%s" % (ci.sha[:8], cj.sha[:8])
                if ci.n_parents >= 2 or cj.n_parents >= 2:
                    self._cls("DUP-MERGE", "%s :: %s" % (tag, subject[:70]))
                    continue
                if not ci.paths or not cj.paths:
                    self._cls("DUP-EMPTY", "%s :: %s" % (tag, subject[:70]))
                    continue
                if subject.startswith(UPLOAD_SUBJECT):
                    self._cls("DUP-UPLOAD", "%s :: %s" % (tag, subject[:70]))
                    continue
                if len(ci.paths) > self.bulk or len(cj.paths) > self.bulk:
                    self._cls("DUP-BULK", "%s :: %d/%d paths :: %s"
                              % (tag, len(ci.paths), len(cj.paths), subject[:70]))
                    continue
                if set(ci.paths) & set(cj.paths):
                    # The dafoam lane's discriminator (L-524 ADDENDUM A): board
                    # repairs and restores legitimately repeat a subject and
                    # their trees OVERLAP. A race's trees cannot overlap.
                    self._cls("DUP-OVERLAP", "%s :: %s" % (tag, subject[:70]))
                    continue
                self.dup_findings.append({
                    "kind": "DUP",
                    "pair": [ci.sha, cj.sha],
                    "distance": j - i,
                    "seconds": abs(ci.ctime - cj.ctime),
                    "subject": subject,
                    "paths": [list(ci.paths)[:6], list(cj.paths)[:6]],
                    "owner": self._owner(ci, cj, subject),
                })

    def _owner(self, ci, cj, subject):
        """Which of a duplicate pair the subject's topic actually fits.

        Reported as an annotation only. It names the likely VICTIM; it is an
        inference from the record, not a caught race (L-524 ADDENDUM A's own
        stated limit), and no exclusion is made on the strength of it.
        """
        sids = ids_in(subject, self.vocab)
        if not sids:
            return "undetermined (subject names no id)"
        hits = [c.sha[:8] for c in (ci, cj)
                if sids & tree_ids(c.paths, self.vocab_ci)]
        if len(hits) == 1:
            return "subject topic fits %s only" % hits[0]
        if not hits:
            return "subject topic fits neither tree"
        return "subject topic fits both trees"

    # -- detector (ii) ------------------------------------------------------
    def run_mm(self):
        for c in self.commits:
            tag = c.sha[:8]
            if c.n_parents >= 2:
                self._cls("MM-MERGE", "%s :: %s" % (tag, c.subject[:70]))
                continue
            if not c.paths:
                self._cls("MM-EMPTY", "%s :: %s" % (tag, c.subject[:70]))
                continue
            if normalize_subject(c.subject).startswith(UPLOAD_SUBJECT):
                self._cls("MM-UPLOAD", "%s :: %s" % (tag, c.subject[:70]))
                continue
            if len(c.paths) > self.bulk:
                self._cls("MM-BULK", "%s :: %d paths :: %s"
                          % (tag, len(c.paths), c.subject[:70]))
                continue
            sids = ids_in(c.subject, self.vocab)
            tids = tree_ids(c.paths, self.vocab_ci)
            if not sids:
                self._cls("MM-NO-SUBJECT-ID (out of population)",
                          "%s :: %s" % (tag, c.subject[:70]))
                continue
            if not tids:
                self._cls("MM-NO-TREE-ID (out of population, records-only tree)",
                          "%s :: %s" % (tag, c.subject[:70]))
                continue
            if sids & tids:
                self._cls("MM-MATCH (clean)", "%s :: %s" % (tag, c.subject[:70]))
                continue
            # BOTH directions of the lab's variant convention: the subject may
            # name the parent of a variant the tree touches ("M1-C" over M1c),
            # or the variants while the tree holds the parent directory (a
            # K0cS/K0cT/K0cX ruling filed under K0c/). Same relation, same
            # digit guard, read from either end.
            variants = sorted({"%s~%s" % (a, b) for a in sids for b in tids
                               if is_variant_of(a, b) or is_variant_of(b, a)})
            if variants and not self.variant_strict:
                # MEASURED class, not a guess: five of the seven MM flags in the
                # last 500 commits are a subject writing "M1-C" over an M1c
                # tree. Named, counted, and recoverable as findings with
                # --variant-strict, which is the audit both ways.
                self._cls("MM-VARIANT-ID (subject names the parent rung of a tree "
                          "variant)", "%s :: %s :: %s" % (tag, ",".join(variants),
                                                          c.subject[:60]))
                continue
            self.mm_findings.append({
                "kind": "MM",
                "sha": c.sha,
                "subject": normalize_subject(c.subject),
                "subject_ids": sorted(sids),
                "tree_ids": sorted(tids),
                "paths": list(c.paths)[:8],
            })

    def run(self):
        self.run_dup()
        self.run_mm()
        return self


# ---------------------------------------------------------------------------
# reporting -- advisory, D539
# ---------------------------------------------------------------------------

def report(screen, label, verbose):
    print("COMMIT-SUBJECT SCREEN -- ADVISORY (docket D539). Findings are")
    print("REPORTED; this screen never refuses a commit and always exits 0.")
    print("  scope        : %s" % label)
    print("  commits      : %d" % len(screen.commits))
    print("  window       : %s commits" % (screen.window or "no limit"))
    print("  vocabulary   : %d identifiers, derived from the repository" % len(screen.vocab))
    print("")
    print("DETECTOR (i) DUP -- same normalized subject, DISJOINT trees, within window")
    if screen.dup_findings:
        for f in screen.dup_findings:
            print("  FLAG %s + %s  dist=%d  dt=%ds" % (f["pair"][0][:8], f["pair"][1][:8],
                                                       f["distance"], f["seconds"]))
            print("       subject: %s" % f["subject"][:150])
            print("       %s" % f["owner"])
            print("       tree A : %s" % ", ".join(f["paths"][0]))
            print("       tree B : %s" % ", ".join(f["paths"][1]))
    else:
        print("  no pair flagged")
    print("  flagged: %d" % len(screen.dup_findings))
    print("")
    print("DETECTOR (ii) MM -- subject names an id, tree names ids, sets DISJOINT")
    if screen.mm_findings:
        for f in screen.mm_findings:
            print("  FLAG %s  subject-ids %s  vs  tree-ids %s"
                  % (f["sha"][:8], f["subject_ids"], f["tree_ids"]))
            print("       subject: %s" % f["subject"][:150])
            print("       paths  : %s" % ", ".join(f["paths"]))
    else:
        print("  no commit flagged")
    print("  flagged: %d" % len(screen.mm_findings))
    print("")
    print("CLASSES NOT FLAGGED -- named and counted, none silently dropped")
    unknown = [n for n in screen.classes if n not in CLASS_NAMES]
    if unknown:
        print("  INSTRUMENT WARNING: undeclared class %s" % unknown)
    for name in list(CLASS_NAMES) + unknown:
        items = screen.classes.get(name, [])
        print("  %-52s %5d" % (name, len(items)))
        if verbose:
            for it in items:
                print("        %s" % it[:160])
    print("")
    print("TOTAL FLAGGED: %d (DUP %d + MM %d).  Exit 0 -- advisory, D539: only "
          "Sanaa may make a screen blocking."
          % (len(screen.dup_findings) + len(screen.mm_findings),
             len(screen.dup_findings), len(screen.mm_findings)))


# ---------------------------------------------------------------------------
# the instrument's check on itself: planted failures, no asserts
# ---------------------------------------------------------------------------

def _emitted_class_names(source):
    """Every literal first argument of a self._cls(...) call, read from the AST.

    Read from the source rather than from a run, so a class that never fired
    is still checked against the declaration.
    """
    out = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if not (isinstance(f, ast.Attribute) and f.attr == "_cls" and node.args):
            continue
        a0 = node.args[0]
        if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
            out.append(a0.value)
        elif isinstance(a0, ast.JoinedStr):
            out.append("<f-string, not statically checkable>")
        elif isinstance(a0, ast.BinOp):
            out.append("<expression, not statically checkable>")
    return out


def count_assert_nodes(source):
    return sum(1 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert))


def _c(sha, subject, paths, parents=1, ctime=0):
    return Commit(sha=(sha * 40)[:40], n_parents=parents, ctime=ctime,
                  subject=subject, paths=tuple(paths))


class Controls:
    """Each control records expected vs observed. No assert: -O cannot delete an if."""

    def __init__(self):
        self.rows = []

    def check(self, name, expected, observed, note=""):
        ok = (expected == observed)
        self.rows.append((ok, name, expected, observed, note))
        return ok

    @property
    def failed(self):
        return [r for r in self.rows if not r[0]]


def selftest(recurse=True):
    src = Path(__file__).read_text()
    ctl = Controls()

    # --- instrument controls ------------------------------------------------
    ctl.check("INSTRUMENT: zero ast.Assert nodes in this file (L-332)",
              0, count_assert_nodes(src),
              "a bare assert would vanish under python3 -O and test nothing")
    ctl.check("INSTRUMENT: git subcommand allowlist is read-only",
              True, GIT_READ_ONLY.isdisjoint({"commit", "add", "update-index",
                                              "write-tree", "commit-tree",
                                              "update-ref", "checkout", "reset"}))
    ctl.check("INSTRUMENT: 'ls-files' is not in the git allowlist",
              False, "ls-files" in GIT_READ_ONLY,
              "D538: the shared index is contaminated; an index-based check "
              "passes VACUOUSLY. Enumeration here is from a TREE only.")

    # --- tokenizer controls -------------------------------------------------
    ctl.check("TOKEN: hyphen expansion recovers D7 from 'D7-DEF-4'",
              True, "D7" in tokens("D7-DEF-4:"))
    ctl.check("TOKEN: hyphenated id survives whole",
              True, "VMFL063-R3" in tokens("VMFL063-R3 regrade"))
    ctl.check("TOKEN: lowercase-carrying rung ids survive",
              True, {"K0c", "T1b", "T23G2Rn2", "D6RF10", "R5C"} <= tokens(
                  "K0c T1b T23G2Rn2 D6RF10 R5C"))
    ctl.check("VOCAB: basenames do NOT create vocabulary",
              set(),
              {"T0", "MD5"} & vocab_from_paths(["a/b/B1_T0.txt", "a/b/X_MD5.txt"]),
              "T0 and MD5 are filename debris and must not become identifiers")
    ctl.check("VOCAB: a rung directory DOES create vocabulary",
              True, "T11" in vocab_from_paths(
                  ["verification/runs/T-family/T11_runs/log.x"]))

    # --- normalization controls --------------------------------------------
    ctl.check("NORM: whitespace collapse makes two spellings equal",
              True, normalize_subject("  a   b ") == normalize_subject("a b"))
    ctl.check("NORM: case is NOT folded (we did not widen the comparator)",
              False, normalize_subject("T4 GRADE") == normalize_subject("t4 grade"))
    ctl.check("NORM: a trailing marker is NOT stripped",
              False, normalize_subject("X [lab-attributed]") == normalize_subject("X"))

    VOCAB = {"T4", "T11", "D4", "D8", "A2", "A3", "K0c", "VMFL063-R3"}

    ctl.check("INSTRUMENT: every emitted class name is declared in CLASS_NAMES",
              [], [n for n in _emitted_class_names(src) if n not in CLASS_NAMES],
              "an undeclared class prints only when non-empty and so hides at 0")

    # --- PLANT 1: duplicate subject on disjoint trees -----------------------
    p1 = Screen([_c("a", "S ONE", ["cases/dafoam/A3/P.md"]),
                 _c("b", "S ONE", ["verification/runs/T-family/T11_runs/log.x"])],
                VOCAB).run()
    ctl.check("PLANT-1 duplicate subject, DISJOINT trees -> 1 DUP finding",
              1, len(p1.dup_findings))

    # --- PLANT 2: subject/tree topic mismatch -------------------------------
    p2 = Screen([_c("c", "T4 GRADE RECORD [lab-attributed]: NOT A RESULT x3",
                    ["verification/runs/T-family/T11_runs/log.x",
                     "docs/COST_CALIBRATION.md"])], VOCAB).run()
    ctl.check("PLANT-2 T4 subject over a T11 tree -> 1 MM finding",
              1, len(p2.mm_findings))
    ctl.check("PLANT-2 names the right two id sets",
              (["T4"], ["T11"]),
              (p2.mm_findings[0]["subject_ids"], p2.mm_findings[0]["tree_ids"])
              if p2.mm_findings else (None, None))

    # --- NEAR-MISS 1: same subject, OVERLAPPING trees -----------------------
    n1 = Screen([_c("d", "S TWO", ["docs/LAB_STATE.md"]),
                 _c("e", "S TWO", ["docs/LAB_STATE.md", "cases/dafoam/A2/x.md"])],
                VOCAB).run()
    ctl.check("NEAR-MISS-1 overlapping trees -> 0 DUP findings",
              0, len(n1.dup_findings))
    ctl.check("NEAR-MISS-1 is classified DUP-OVERLAP, not dropped",
              1, len(n1.classes.get("DUP-OVERLAP", [])))

    # --- NEAR-MISS 2: subject names an id the tree DOES touch ---------------
    n2 = Screen([_c("f", "T11 grade landed", ["verification/runs/T-family/T11_runs/g.md"])],
                VOCAB).run()
    ctl.check("NEAR-MISS-2 subject id present in tree -> 0 MM findings",
              0, len(n2.mm_findings))
    ctl.check("NEAR-MISS-2 is classified MM-MATCH, not dropped",
              1, len(n2.classes.get("MM-MATCH (clean)", [])))

    # --- OUT OF POPULATION --------------------------------------------------
    n3 = Screen([_c("g", "tidy up the readme", ["cases/dafoam/A2/x.md"])], VOCAB).run()
    ctl.check("OUT-OF-POP subject names no id -> 0 findings",
              0, len(n3.mm_findings))
    ctl.check("OUT-OF-POP subject-no-id is its own counted class",
              1, len(n3.classes.get("MM-NO-SUBJECT-ID (out of population)", [])))
    n4 = Screen([_c("h", "T4 record filed", ["docs/LESSONS.md"])], VOCAB).run()
    ctl.check("OUT-OF-POP records-only tree -> 0 findings",
              0, len(n4.mm_findings))
    ctl.check("OUT-OF-POP tree-no-id is its own counted class",
              1, len(n4.classes.get(
                  "MM-NO-TREE-ID (out of population, records-only tree)", [])))

    # --- TREE-SIDE ASYMMETRY controls ---------------------------------------
    ci = Screen([_c("v", "ARM detached L3 autograder (setsid PPID=1) + board 38",
                    ["docs/LAB_STATE.md",
                     "verification/runs/T-family/T23G2R_runs/autograde_t23g2r_l3.sh"])],
                {"L3", "T23G2R"}).run()
    ctl.check("TREE-CI a lower-case spelling in a filename satisfies the id",
              (0, 1), (len(ci.mm_findings), len(ci.classes.get("MM-MATCH (clean)", []))),
              "5a8f80e6 measured: the tree spells the rung l3, the subject L3")
    ctl.check("SUBJECT side stays case-SENSITIVE (the widening is one-way)",
              set(), ids_in("t4 grade record", {"T4"}))

    # --- VARIANT-ID class and its digit guard --------------------------------
    var = Screen([_c("w", "closure M1-C VERDICT: GATE FAIL governed by G2",
                     ["cases/RANS_LES_closure_models/M1c_multimodel_sweep/R.md"])],
                 {"M1", "M1c", "G2"}).run()
    ctl.check("VARIANT M1 subject over an M1c tree -> 0 findings, named class",
              (0, 1), (len(var.mm_findings),
                       len(var.classes.get("MM-VARIANT-ID (subject names the parent "
                                           "rung of a tree variant)", []))))
    var2 = Screen([_c("x", "closure M1-C VERDICT",
                      ["cases/RANS_LES_closure_models/M1c_multimodel_sweep/R.md"])],
                  {"M1", "M1c"}, variant_strict=True).run()
    ctl.check("VARIANT --variant-strict puts the same commit back as a finding",
              1, len(var2.mm_findings))
    dg = Screen([_c("y", "T1 grade record",
                    ["verification/runs/T-family/T11_runs/log.x"])],
                {"T1", "T11"}).run()
    ctl.check("VARIANT digit guard: T1 over a T11 tree is STILL a finding",
              1, len(dg.mm_findings),
              "T1 and T11 are different rungs; the T4/T11 shape must survive")
    rev = Screen([_c("u", "K0cS/K0cT/K0cX model-form GATE FAILs -> state (b)",
                     ["docs/campaigns/F14-cooling-ladder/K0c_SUCCESSOR.md"])],
                 {"K0c", "K0cS", "K0cT", "K0cX", "F14"}).run()
    ctl.check("VARIANT the reverse direction (tree holds the PARENT) is the "
              "same class",
              (0, 1), (len(rev.mm_findings),
                       len(rev.classes.get("MM-VARIANT-ID (subject names the parent "
                                           "rung of a tree variant)", []))))
    ctl.check("VARIANT is_variant_of is asymmetric and digit-guarded",
              (True, True, False, False),
              (is_variant_of("M1", "M1c"), is_variant_of("K0", "K0cG"),
               is_variant_of("T1", "T11"), is_variant_of("M1c", "M1")))

    # --- EXCLUSION CLASSES --------------------------------------------------
    m = Screen([_c("i", "S THREE", ["cases/dafoam/A2/x.md"], parents=2),
                _c("j", "S THREE", ["verification/runs/T-family/T11_runs/y"])],
               VOCAB).run()
    ctl.check("EXCL merge commit -> 0 DUP findings, class DUP-MERGE",
              (0, 1), (len(m.dup_findings), len(m.classes.get("DUP-MERGE", []))))
    e = Screen([_c("k", "S FOUR", []),
                _c("l", "S FOUR", ["cases/dafoam/A2/x.md"])], VOCAB).run()
    ctl.check("EXCL empty commit -> 0 DUP findings, class DUP-EMPTY",
              (0, 1), (len(e.dup_findings), len(e.classes.get("DUP-EMPTY", []))))
    u = Screen([_c("m", UPLOAD_SUBJECT, ["a/b.txt"]),
                _c("n", UPLOAD_SUBJECT, ["c/d.txt"])], VOCAB).run()
    ctl.check("EXCL GitHub upload -> 0 DUP findings, class DUP-UPLOAD",
              (0, 1), (len(u.dup_findings), len(u.classes.get("DUP-UPLOAD", []))))
    big = ["cases/dafoam/A2/f%03d.md" % k for k in range(BULK_PATHS + 1)]
    b = Screen([_c("o", "T4 sweep", big)], VOCAB).run()
    ctl.check("EXCL sweep/bulk commit -> 0 MM findings, class MM-BULK",
              (0, 1), (len(b.mm_findings), len(b.classes.get("MM-BULK", []))))
    ser = Screen([_c("p", "ADDENDUM", ["cases/dafoam/A2/a.md"]),
                  _c("q", "ADDENDUM", ["cases/dafoam/A3/b.md"]),
                  _c("r", "ADDENDUM", ["verification/runs/T-family/T11_runs/c"])],
                 VOCAB).run()
    ctl.check("EXCL addenda series (3x in window) -> 0 DUP findings, class DUP-SERIES",
              (0, 1), (len(ser.dup_findings), len(ser.classes.get("DUP-SERIES", []))))

    # --- WINDOW controls: the parameter must actually bite -------------------
    filler = [_c("z", "filler %d" % k, ["cases/dafoam/A2/f%d.md" % k]) for k in range(60)]
    far = [_c("s", "S FIVE", ["cases/dafoam/A3/x.md"])] + filler + \
          [_c("t", "S FIVE", ["verification/runs/T-family/T11_runs/y"])]
    ctl.check("WINDOW distance 61 > 50 -> 0 findings",
              0, len(Screen(far, VOCAB, window=50).run().dup_findings))
    ctl.check("WINDOW distance 61 is classified DUP-OUT-OF-WINDOW, not dropped",
              1, len(Screen(far, VOCAB, window=50).run().classes
                     .get("DUP-OUT-OF-WINDOW", [])))
    ctl.check("WINDOW same pair with --window 0 (no limit) -> 1 finding",
              1, len(Screen(far, VOCAB, window=0).run().dup_findings))

    # --- -O PARITY: this file, under the other interpreter flag -------------
    if recurse:
        flag = [] if not __debug__ else ["-O"]
        proc = subprocess.run([sys.executable] + flag +
                              [str(Path(__file__).resolve()), "--selftest", "--no-recurse"],
                              capture_output=True, text=True)
        mine = len(ctl.rows)  # this run's controls, minus the parity row itself
        theirs = None
        for line in proc.stdout.split("\n"):
            if line.startswith("SELFTEST CONTROLS: "):
                theirs = int(line.split()[2])
        ctl.check("PARITY: sibling interpreter (%s) rc" %
                  ("python3 -O" if flag else "python3"), 0, proc.returncode)
        ctl.check("PARITY: sibling interpreter control count == mine",
                  mine, theirs,
                  "if these differ the SELFTEST is defective, not curious")

    print("SELFTEST CONTROLS: %d" % len(ctl.rows))
    for ok, name, exp, obs, note in ctl.rows:
        print("  %-4s %s" % ("ok" if ok else "FAIL", name))
        if not ok:
            print("       expected %r, observed %r" % (exp, obs))
            if note:
                print("       note: %s" % note)
    if ctl.failed:
        print("SELFTEST FAILED: %d of %d controls" % (len(ctl.failed), len(ctl.rows)))
        print("A planted case the detector cannot see is a DEFECT IN THE "
              "DETECTOR. Do not adjust the plant.")
        return 2
    plants = sum(1 for r in ctl.rows if r[1].startswith("PLANT-"))
    misses = sum(1 for r in ctl.rows if r[1].startswith(("NEAR-MISS", "OUT-OF-POP")))
    excl = sum(1 for r in ctl.rows if r[1].startswith("EXCL"))
    print("SELFTEST PASS: %d controls, each with a stated expectation -- "
          "%d planted-failure rows, %d near-miss rows, %d exclusion-class rows."
          % (len(ctl.rows), plants, misses, excl))
    return 0


# ---------------------------------------------------------------------------

def main(argv):
    ap = argparse.ArgumentParser(
        description=("Screen commit SUBJECTS against their TREES (L-524). "
                     "ADVISORY per docket D539: reports, never refuses."))
    ap.add_argument("--repo", default=str(REPO_DEFAULT))
    ap.add_argument("--rev", default="main", help="rev to scan (default main)")
    ap.add_argument("--count", type=int, default=DEFAULT_COUNT,
                    help="number of commits (default %d)" % DEFAULT_COUNT)
    ap.add_argument("--all-history", action="store_true", help="no commit limit")
    ap.add_argument("--range", dest="rng", default=None,
                    help="explicit git range, e.g. A..B (overrides --rev/--count)")
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW,
                    help="DUP window in commits; 0 = no limit (default %d)"
                         % DEFAULT_WINDOW)
    ap.add_argument("--bulk", type=int, default=BULK_PATHS,
                    help="paths above which a commit is a sweep (default %d)" % BULK_PATHS)
    ap.add_argument("--only", choices=["dup", "mm", "both"], default="both")
    ap.add_argument("--variant-strict", action="store_true",
                    help="report MM-VARIANT-ID as findings instead of as a class")
    ap.add_argument("--verbose", action="store_true", help="list every class member")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-recurse", action="store_true",
                    help="internal: suppress the selftest's -O parity child")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest(recurse=not a.no_recurse)

    n_assert = count_assert_nodes(Path(__file__).read_text())
    if n_assert:
        print("REFUSED (instrument): %d assert(s) present; python3 -O would "
              "delete them (L-332)." % n_assert)
        return 2

    repo = Path(a.repo)
    count = None if a.all_history else a.count
    commits = read_log(repo, a.rev, count, a.rng)
    if not commits:
        # A screen handed an empty history must not report "clean".
        raise Refusal("git log returned no commits for the requested scope; "
                      "a subject screen that sees nothing must not call it clean")

    tip = a.rng.split("..")[-1] if a.rng else a.rev
    tree_paths = git(["ls-tree", "-r", "--name-only", tip, "--"] +
                     list(VOCAB_PREFIXES), repo).split("\n")
    vocab_tip = vocab_from_paths([p for p in tree_paths if p], VOCAB_PREFIXES)
    vocab_hist = vocab_from_paths(
        [p for c in commits for p in c.paths], VOCAB_PREFIXES) - vocab_tip
    vocab = vocab_tip | vocab_hist

    screen = Screen(commits, vocab, window=a.window, bulk=a.bulk,
                    variant_strict=a.variant_strict)
    if a.only in ("dup", "both"):
        screen.run_dup()
    if a.only in ("mm", "both"):
        screen.run_mm()

    label = a.rng if a.rng else ("%s, last %s commits" % (a.rev, count or "all"))
    if a.json:
        print(json.dumps({
            "scope": label,
            "commits": len(commits),
            "window": a.window,
            "vocab_from_tip": len(vocab_tip),
            "vocab_from_scanned_history_only": sorted(vocab_hist),
            "dup_findings": screen.dup_findings,
            "mm_findings": screen.mm_findings,
            "classes": {k: len(screen.classes.get(k, [])) for k in CLASS_NAMES},
            "advisory": "D539 -- reports only; exit 0 regardless of findings",
        }, indent=1))
    else:
        print("  vocabulary sources: %d from the tip tree, %d more from the "
              "scanned commits' own paths" % (len(vocab_tip), len(vocab_hist)))
        report(screen, label, a.verbose)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print("REFUSED (instrument could not run, NOT a verdict on any commit): %s" % exc)
        sys.exit(2)
