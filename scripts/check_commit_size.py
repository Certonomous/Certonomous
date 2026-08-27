#!/usr/bin/env python3
"""Commit-size guard. REPORTS on a tree; it never acts on one.

Built to docs/standards/COMMIT_SIZE_GUARD.md, which was frozen at 9803334a
BEFORE this file existed, so this guard could not be shaped to pass its own
test. Sanaa's standing directives 2026-08-27T16:54Z section 1: "pre-commit
guard blocks >50 files or >5 MB without a manifest" and "logs and attempt dirs
stay out of git".

WHAT THIS IS NOT, STATED FIRST BECAUSE IT IS THE POINT OF THE INSTRUMENT
-----------------------------------------------------------------------
It never kills, never deletes, never touches git in a writing subcommand,
never writes an index, never rewrites a path, never infers intent, and it
NEVER GENERATES THE MANIFEST FOR YOU. A guard that fixes its own finding
cannot be trusted to report it (spec section 3). The only child processes it
starts are `git` in a READ-ONLY subcommand allowlist enforced at the one call
site, and -- inside `--selftest` only -- this file itself, to prove a caller
can detect its refusal.

EXIT CODES
    0   accept
    2   refuse (at least one clause fired), or the selftest failed
    1   usage error

The CALLER MUST TEST THE EXIT CODE. `set -e` is NOT in force in this harness:
measured here 2026-08-27, `python3 -c "raise SystemExit(1)"; echo REACHED`
prints REACHED at the top level, and `bash -c '<failing cmd>; echo X'` exits 0
-- the failure is swallowed whole. A refusal that is only printed is not a
gate (L-314 Instance 1; a cfd assertion aborted at da7e1477 and the commit
landed anyway). Every refusal here is a `raise` or a `sys.exit(2)`, never an
`assert`, because `python3 -O` deletes asserts (L-332); `--selftest` parses
this file's own AST and refuses if a single `ast.Assert` node exists.

ENUMERATION IS FROM THE TREE, NEVER FROM THE INDEX
--------------------------------------------------
`git ls-files` enumerates the INDEX. The shared index in this repository is
contaminated (379 staged deletions across every team on 2026-08-27, files all
present on disk), so any check built on it reports "nothing to verify" and
passes VACUOUSLY -- a cfd freeze check returned "0 match / 0 differ" for
exactly that reason. This guard enumerates with `git diff-tree -r` between two
TREES and never calls `ls-files`; `ls-files` is absent from the read-only
allowlist and a selftest control greps this source to prove it is absent from
the file as well. A guard handed an EMPTY file list REFUSES under `EMPTY`
rather than reporting "small enough": a size guard that sees nothing must not
call it small.

USAGE
    python3 scripts/check_commit_size.py --base <tree-ish> --tree <tree-ish>
    python3 scripts/check_commit_size.py --commit <sha>   # replay vs parent
    python3 scripts/check_commit_size.py --selftest
"""
import sys

# `python3 -O` refusal AT ENTRY. This file is a comparator that is EXECUTED and
# has no importers, so the module-level idiom of cases/F25_DUCT3D/grade_f25.py
# (:43-:46) applies to it directly. R-AGE-CWD's sibling ruling: an IMPORTED
# module may not carry a module-level sys.exit(2) -- it would fire on import --
# and scopes the bail to --selftest instead. This file is not that case.
if not __debug__:
    sys.stderr.write(
        "REFUSED: check_commit_size.py must not run under `python3 -O` or "
        "PYTHONOPTIMIZE. Re-run under plain `python3`.\n")
    sys.exit(2)

import ast
import json
import argparse
import fnmatch
import subprocess
import tempfile
from pathlib import Path
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Thresholds, from the frozen spec's table. Not tunable at the command line:
# a threshold a caller can move is not a threshold.
# ---------------------------------------------------------------------------
COUNT_MAX = 50            # spec: refuses when > 50 files added or modified
BYTES_MAX = 5_000_000     # spec: "> 5 MB total added bytes"

# SPEC GAP, DECLARED NOT DECIDED: the spec writes "5 MB" without fixing decimal
# or binary. 5 * 1024 * 1024 = 5,242,880 is the LOOSER reading and would let
# 242,880 more bytes through, so it is not taken here. The stricter decimal
# reading is used and reported upward for ruling; a guard's implementer does
# not resolve an ambiguity in the direction that widens it.

LOG_BASENAME_PATTERNS = ("log.*", "*.log")            # spec: log.* , */log.* , *.log
ATTEMPT_DIR_PATTERNS = ("attempt*", "*_attempt*")     # spec: attempt*/ , *_attempt*/
ATTEMPT_DIR_EXACT = ("scratch", "__pycache__")        # spec: scratch/ , __pycache__/

# The manifest's FILENAME is not fixed by the spec. SPEC GAP, DECLARED AND
# REFERRED, NOT RESOLVED BY THE IMPLEMENTER. Measured 2026-08-27: HEAD carries
# 18 tracked files whose basename contains MANIFEST, across at least eight
# UNRELATED purposes -- TOOLCHAIN_MANIFEST.txt, VM2026R1_SHA256_MANIFEST.txt,
# AV1R_RENAME_MANIFEST.txt, BUILD_MANIFEST.txt, HEAVY_ARTEFACT_MANIFEST.md,
# MANIFEST.json, MANIFEST_t1..t4.txt, MANIFEST.md. A basename PATTERN therefore
# lets an artifact with nothing to do with this commit exempt it from COUNT and
# BYTES -- a hole, and the selftest caught it: an early draft of this guard
# matched 05241ab2's two HEAVY_ARTEFACT_MANIFEST.md files, which manifest paths
# deliberately NOT at HEAD, and wrongly exempted that commit's COUNT.
#
# So the name is EXACT and reserved: COMMIT_MANIFEST.md, which occurs ZERO
# times in HEAD today. That is the strictest available reading -- today it
# exempts nothing and every team must add the file to claim the exemption --
# and strictness cannot be a silent widening. Choosing a looser name is the
# owner's call, not this implementer's.
MANIFEST_BASENAMES = ("COMMIT_MANIFEST.md",)

GIT_READ_ONLY = frozenset({"cat-file", "rev-parse", "ls-tree", "diff-tree"})


class Refusal(Exception):
    """A condition that must stop the instrument under ANY interpreter flag."""


class Change(NamedTuple):
    """One path in a tree-to-tree diff. `status` is A, M or D."""
    path: str
    status: str
    new_size: int
    old_size: int


class CommitMeta(NamedTuple):
    """What EMPTY needs to know about the commit, and nothing else. Read from
    `git cat-file -p <sha>` (parent lines and the tree line), so no writing or
    index-reading subcommand is involved."""
    n_parents: int
    tree_equals_first_parent: bool


class Mutations(NamedTuple):
    """SELFTEST ONLY. Each field reintroduces a specific defect so the control
    that catches it can be shown to FLIP. The command-line path never
    constructs anything but the all-False default, and a control proves it."""
    disable_count: bool = False
    disable_bytes: bool = False
    disable_logs: bool = False
    disable_attempt: bool = False
    manifest_exempts_logs: bool = False      # the defect the spec FORBIDS
    disable_runs_exemption: bool = False     # AMENDMENT 1 (d), shown load-bearing
    widen_merge_carveout: bool = False       # AMENDMENT 2: carve-out on ANY parent count
    disable_logs_runs_exemption: bool = False   # AMENDMENT 3, shown load-bearing


CLEAN = Mutations()


def _git(args, cwd):
    """One READ-ONLY git subcommand. Anything else is refused at this call
    site rather than avoided by discipline. Written as a `raise`, never an
    `assert`: under -O an assert here would leave an unguarded passthrough."""
    if not args:
        raise Refusal("GIT-READ-ONLY: empty git argv")
    if args[0] not in GIT_READ_ONLY:
        raise Refusal(
            "GIT-READ-ONLY: subcommand %r is not in the read-only allowlist %s. "
            "This guard never writes to git and never reads the INDEX -- "
            "`ls-files` is deliberately absent, because the shared index is "
            "contaminated and an index-based check passes vacuously."
            % (args[0], sorted(GIT_READ_ONLY)))
    return subprocess.run(["git", "-C", str(cwd)] + args,
                          capture_output=True, text=True)


# ---------------------------------------------------------------------------
# Path predicates. Each is the spec's pattern list and nothing more.
# ---------------------------------------------------------------------------

# AMENDMENT 3, 2026-08-27. cfd-supervisor is the named Owner of the spec; the
# change is the Owner's, not the implementer's. SANAA APPROVED IT at 8ed55f26
# (docs/LAB_STATE.md, CHIEF section), in her ruling's words: verification/runs/**
# /log.* is EXEMPT from the LOGS clause; BYTES (5,000,000) and COUNT (50) keep
# catching bulk.
#
# THE MEASUREMENT THAT EARNED IT is cfd's own, boarded at 532da5d9 and recorded
# in AMENDMENT 2 (1) of docs/standards/COMMIT_SIZE_GUARD.md: on 200 real commits
# LOGS scored 0 TRUE POSITIVES and 14 FALSE POSITIVES. Zero of the 14 carried a
# single log path OUTSIDE verification/runs/ -- every firing was correctly filed
# run output. The archetype 05241ab2 is a TRUE positive on BYTES (276,711,923
# added bytes) and a FALSE one on LOGS: its defect was never that a log was in
# git, it was 276.7 MB of it. And these logs are what the lab's own records
# cite -- CLAUDE.md standing rule 4's completion evidence (rc = 0, an `End`
# line, last time == endTime, an ExecutionTime count == endTime) is READ FROM
# the solver log, so evicting solver logs from git would make the lab's own
# completion rule unverifiable from the repository.
#
# WHAT IS NOT CHANGED, and is proven not changed by controls L3b/L3c/L3d below:
# LOGS is STILL NOT EXEMPTIBLE BY MANIFEST; it still fires on every log path
# outside a run tree; and BYTES and COUNT are untouched and still fire on the
# very same run-tree paths, so the exemption did not open a bulk hole.
#
# The prefix test is the SAME RUN_TREE_PREFIX constant AMENDMENT 1 (d) uses,
# defined a few lines below (resolved at call time, not at def time). One
# constant deliberately: two prefix tests would be two exemptions drifting apart.
def is_log_path(path, mut=None):
    if path.startswith(RUN_TREE_PREFIX) and not (mut and mut.disable_logs_runs_exemption):
        return False                       # AMENDMENT 3: filed run outputs
    base = path.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatchcase(base, pat) for pat in LOG_BASENAME_PATTERNS)


# AMENDMENT 1, 2026-08-27, cfd-supervisor as named Owner of the spec, on the
# measurements below. Both changes are recorded in the spec's dated amendment;
# neither was taken by the implementer.
#
# (c) LEADING-DOT VARIANTS MATCH. A hidden attempt directory is still an
#     attempt directory, and a leading dot is precisely how one would evade the
#     clause. Found live: 05241ab2 landed .attempt1_stale/ , which the frozen
#     pattern did not match.
#
# (d) ATTEMPT DOES NOT MATCH UNDER verification/runs/. That is the CORRECT
#     filing location for run outputs (FILING_CHARTER), and attemptN_<descriptor>/
#     is this lab's legitimate convention for successive attempts at a rung.
#     The clause was written to keep SCRATCH attempt directories out of git, not
#     to reject FILED run outputs; as frozen it would have refused every
#     legitimate re-attempt the lab files the moment it went blocking, and the
#     0/200 ATTEMPT score hid that entirely because those paths simply were not
#     re-touched in the sample. The clause keeps its teeth everywhere else.
RUN_TREE_PREFIX = "verification/runs/"


def is_attempt_path(path, mut=None):
    if path.startswith(RUN_TREE_PREFIX) and not (mut and mut.disable_runs_exemption):
        return False                       # ruling (d): filed run outputs
    for comp in path.split("/")[:-1]:      # DIRECTORY components only
        bare = comp[1:] if comp.startswith(".") else comp   # ruling (c)
        if bare in ATTEMPT_DIR_EXACT:
            return True
        if any(fnmatch.fnmatchcase(bare, pat) for pat in ATTEMPT_DIR_PATTERNS):
            return True
    return False


def is_manifest_path(path):
    return path.rsplit("/", 1)[-1] in MANIFEST_BASENAMES


def manifest_is_valid(text):
    """Spec section 2: a manifest names what is being landed and why, one line
    per group, WITH A TOTAL. A file called MANIFEST that says nothing is not a
    manifest, so the total is required and checked."""
    if not text or not text.strip():
        return False
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        return False
    return any("total" in l.lower() for l in lines)


def added_bytes_of(change):
    """Spec: 'total added bytes'. For an add, the whole blob. For a
    modification, the GROWTH -- the literal reading. The full-new-blob reading
    is also computed and printed as a diagnostic so nothing is hidden."""
    if change.status == "A":
        return change.new_size
    if change.status == "M":
        return max(0, change.new_size - change.old_size)
    return 0


# ---------------------------------------------------------------------------
# The evaluation. PURE: it takes a list of Change and the text of any manifest
# in the same tree, and returns named findings. It touches no git, no disk and
# no clock, so the selftest can synthesise every control in memory and the git
# adapter below is the only thing that has to be exercised against a real tree.
# ---------------------------------------------------------------------------

def evaluate(changes, manifest_texts=None, mut=CLEAN, meta=None):
    manifest_texts = manifest_texts or {}
    findings = []
    notes = []

    # INSTRUMENT INTEGRITY, ordered by cfd-supervisor 2026-08-27 and distinct
    # from the four commit-property clauses of the frozen spec: a guard handed
    # nothing must not report "small enough". `git ls-files` against the
    # contaminated shared index is exactly how a guard comes to see nothing.
    if not changes:
        # AMENDMENT 2 (verification D538/D539, relayed by the Owner): a TRUE
        # MERGE whose tree equals its first parent's yields zero changed paths
        # through no fault of the committer, and EMPTY would fire spuriously.
        # Carved out -- but NOT SILENTLY. A carve-out that hides is a hole.
        # MEASURED BEFORE SHIPPING, and it CORRECTS the premise the carve-out
        # was ordered on: the claim was that this repository has linear history
        # by construction, so a merge is anomalous. Merges are RARE here, not
        # absent -- 15 in the last 500 commits, 3.0%, measured. The lane work
        # under the private-index protocol never merges, which is what makes a
        # merge worth REPORTING; but at 3% a silent carve-out would have hidden
        # real cases, so the note below is load-bearing rather than decorative.
        merge_carved = (meta is not None
                        and meta.tree_equals_first_parent
                        and (meta.n_parents >= 2 or mut.widen_merge_carveout))
        if merge_carved:
            notes.append(
                "MERGE: %d-parent commit whose tree equals its first parent's -- "
                "zero changed paths, EMPTY skipped. This repository has linear "
                "history by construction, so a merge is itself anomalous and is "
                "reported rather than passed over in silence." % meta.n_parents)
            return findings, notes
        findings.append(
            "EMPTY: the guard was handed ZERO changed paths. That is not an "
            "accept -- it is a guard that cannot see. A size guard reporting on "
            "an empty enumeration passes vacuously; check that the tree pair is "
            "right and that nothing enumerated the INDEX (`git ls-files`) "
            "instead of the TREE.")
        return findings, notes

    live = [c for c in changes if c.status in ("A", "M")]
    n_live = len(live)
    total_added = sum(added_bytes_of(c) for c in live)
    gross_new = sum(c.new_size for c in live)

    valid_manifests = sorted(p for p, t in manifest_texts.items() if manifest_is_valid(t))
    named_manifests = sorted(c.path for c in live if is_manifest_path(c.path))
    has_manifest = bool(valid_manifests)

    notes.append("files added or modified: %d (threshold %d)" % (n_live, COUNT_MAX))
    notes.append("added bytes: %d (threshold %d); gross new-blob bytes: %d"
                 % (total_added, BYTES_MAX, gross_new))
    if named_manifests and not has_manifest:
        notes.append("manifest-named paths present but NONE is a valid manifest "
                     "(needs >= 2 non-empty lines and a total): %s" % named_manifests)
    elif has_manifest:
        notes.append("valid manifest(s): %s -- exempts COUNT and BYTES ONLY"
                     % valid_manifests)

    # --- COUNT ------------------------------------------------------------
    if n_live > COUNT_MAX and not mut.disable_count:
        if has_manifest:
            notes.append("COUNT would have fired (%d > %d) and is EXEMPT: a valid "
                         "manifest explains the bulk." % (n_live, COUNT_MAX))
        else:
            findings.append(
                "COUNT: %d files added or modified, over the threshold of %d, "
                "with no manifest IN THIS COMMIT. A COMMIT_MANIFEST.md that "
                "already exists in the repository does NOT count: the manifest "
                "must be Added or Modified by the very commit it explains. Land "
                "one naming what is being landed and why -- one line per group, "
                "with a total -- or split the commit. This guard does not write "
                "the manifest for you." % (n_live, COUNT_MAX))

    # --- BYTES ------------------------------------------------------------
    if total_added > BYTES_MAX and not mut.disable_bytes:
        if has_manifest:
            notes.append("BYTES would have fired (%d > %d) and is EXEMPT by manifest."
                         % (total_added, BYTES_MAX))
        else:
            findings.append(
                "BYTES: %d added bytes, over the threshold of %d, with no "
                "manifest IN THIS COMMIT (a pre-existing one does not count; it "
                "must be Added or Modified here). Bulk evidence is filed by digest OUTSIDE "
                "git (/home/ubuntu/certonomous-runs/, docs/LOCATIONS.md); a "
                "manifest explains bulk that genuinely belongs in the repository."
                % (total_added, BYTES_MAX))

    # --- LOGS -- NOT EXEMPTIBLE BY MANIFEST -------------------------------
    logs = sorted(c.path for c in live if is_log_path(c.path, mut))
    if logs and not mut.disable_logs:
        exempt = has_manifest and mut.manifest_exempts_logs
        if exempt:
            notes.append("LOGS suppressed by a manifest -- THIS IS THE DEFECT THE "
                         "SPEC FORBIDS and exists here only as a selftest mutant.")
        else:
            findings.append(
                "LOGS: %d path(s) match log.* / */log.* / *.log OUTSIDE "
                "verification/runs/ , and logs stay out of git (Sanaa section 1). "
                "A MANIFEST DOES NOT EXEMPT THIS: a manifest explains bulk, it "
                "does not make a solver log a repository artifact. File the log "
                "by digest outside git. Paths UNDER verification/runs/ are EXEMPT "
                "(AMENDMENT 3, approved by Sanaa at 8ed55f26 on a measured 0 true "
                "/ 14 false split over 200 commits); BYTES and COUNT still catch "
                "bulk there. First 5: %s" % (len(logs), logs[:5]))

    # --- ATTEMPT -- NOT EXEMPTIBLE BY MANIFEST ----------------------------
    att = sorted(c.path for c in live if is_attempt_path(c.path, mut))
    if att and not mut.disable_attempt:
        findings.append(
            "ATTEMPT: %d path(s) sit under attempt*/ , *_attempt*/ , scratch/ or "
            "__pycache__/ (leading-dot variants included) and attempt "
            "directories stay out of git (Sanaa section 1). A MANIFEST DOES NOT "
            "EXEMPT THIS. Paths under verification/runs/ are EXEMPT -- that is "
            "the correct filing location for run outputs and attemptN_<descriptor>/ "
            "is the lab's convention there (AMENDMENT 1). First 5: %s"
            % (len(att), att[:5]))

    return findings, notes


# ---------------------------------------------------------------------------
# The git adapter. The ONLY part that talks to a repository. Enumerates with
# diff-tree between two TREES; `ls-files` is not reachable from here.
# ---------------------------------------------------------------------------

def blob_size(sha, root, cache):
    if sha in cache:
        return cache[sha]
    if not sha or set(sha) == {"0"}:
        cache[sha] = 0
        return 0
    out = _git(["cat-file", "-s", sha], root)
    size = int(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else 0
    cache[sha] = size
    return size


def changes_from_trees(base, tree, root):
    """Enumerate A/M/D between two tree-ish objects. --no-renames because
    rename detection collapses an add+delete pair into one 'modified' line and
    hides a path from exactly the count this guard is measuring."""
    out = _git(["diff-tree", "-r", "--no-renames", "--root", base, tree], root)
    if out.returncode != 0:
        raise Refusal("DIFF-TREE: could not diff %s..%s in %s: %s"
                      % (base, tree, root, out.stderr.strip()))
    cache = {}
    changes = []
    for line in out.stdout.splitlines():
        if not line.startswith(":"):
            continue
        meta, _, path = line.partition("\t")
        path = path.strip()
        fields = meta[1:].split()
        if len(fields) < 5 or not path:
            continue
        old_sha, new_sha, status = fields[2], fields[3], fields[4][0]
        changes.append(Change(path, status,
                              blob_size(new_sha, root, cache),
                              blob_size(old_sha, root, cache)))
    return changes


def manifest_texts_from_tree(changes, tree, root):
    texts = {}
    for c in changes:
        if c.status in ("A", "M") and is_manifest_path(c.path):
            out = _git(["cat-file", "-p", "%s:%s" % (tree, c.path)], root)
            if out.returncode == 0:
                texts[c.path] = out.stdout
    return texts


def commit_meta_from_sha(sha, root):
    """Parent count and tree equality, read with cat-file only."""
    out = _git(["cat-file", "-p", sha], root)
    if out.returncode != 0:
        return None
    tree = None
    parents = []
    for line in out.stdout.splitlines():
        if line.startswith("tree "):
            tree = line.split()[1]
        elif line.startswith("parent "):
            parents.append(line.split()[1])
        elif not line.strip():
            break
    if tree is None:
        return None
    eq = False
    if parents:
        pout = _git(["cat-file", "-p", parents[0]], root)
        if pout.returncode == 0:
            for line in pout.stdout.splitlines():
                if line.startswith("tree "):
                    eq = (line.split()[1] == tree)
                    break
    return CommitMeta(len(parents), eq)


def repo_root(start):
    out = _git(["rev-parse", "--show-toplevel"], start)
    if out.returncode != 0:
        raise Refusal("REPO-ROOT: %s is not inside a git repository" % start)
    return Path(out.stdout.strip())


def report(findings, notes, label):
    for note in notes:
        print("    note: " + note)
    if findings:
        print("REFUSED %s" % label)
        for f in findings:
            print("    " + f)
        print("    ADVISORY ROLLOUT (spec section 5): for one working session "
              "refusals are REPORTED and commits proceed, so the false-positive "
              "rate is measured on real traffic and boarded first. This guard "
              "becomes blocking only after that, and never on an agent's "
              "say-so -- not the author's, not a supervisor's.")
        return 2
    # Printed INSIDE the accepting branch: deleting the checks deletes the claim.
    print("ACCEPTED %s -- COUNT, BYTES, LOGS and ATTEMPT all clear on a "
          "non-empty enumeration of %s" % (label, label))
    return 0


# ---------------------------------------------------------------------------
# The instrument's check on ITSELF.
# ---------------------------------------------------------------------------

def count_assert_nodes(source):
    return sum(1 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert))


def selftest():
    if not __debug__:
        print("REFUSED: --selftest must not run under -O")
        return 2
    root = repo_root(Path(__file__).resolve().parent)
    problems = []
    lines = []
    src = Path(__file__).read_text()

    # --- 0a: zero asserts, and the counter shown able to see a non-zero ----
    n = count_assert_nodes(src)
    if n:
        problems.append("AST-NO-ASSERT: this guard contains %d assert(s); -O "
                        "deletes every one (L-332)." % n)
    else:
        lines.append("AST-NO-ASSERT: zero `assert` nodes in this guard (L-332).")
    if count_assert_nodes("def f(x):\n    assert x > 0\n    return x\n") != 1:
        problems.append("CONTROL FAILED (ast counter): could not see a planted "
                        "assert, so its zero above means nothing.")
    else:
        lines.append("CONTROL FIRED (ast counter): saw the 1 planted assert in a "
                     "synthetic source, so the zero above is a reading.")

    # --- 0b: the index is never consulted ---------------------------------
    # Mechanical, not textual: every _git() CALL SITE is read out of the AST and
    # its subcommand literal collected, so prose mentioning the index reader
    # cannot make this control pass or fail. A textual grep got this wrong first.
    subcmds = set()
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_git" and node.args
                and isinstance(node.args[0], ast.List) and node.args[0].elts
                and isinstance(node.args[0].elts[0], ast.Constant)):
            subcmds.add(node.args[0].elts[0].value)
    if not subcmds:
        problems.append("CONTROL FAILED (no-ls-files): the AST reader found ZERO "
                        "_git call sites, so its verdict is a blind spot, not a "
                        "reading.")
    elif "ls-files" in subcmds:
        problems.append("CONTROL FAILED (no-ls-files): a _git call site reads the "
                        "INDEX. The shared index is contaminated and an "
                        "index-based enumeration passes VACUOUSLY.")
    elif "ls-files" in GIT_READ_ONLY:
        problems.append("CONTROL FAILED (no-ls-files): ls-files is in the allowlist.")
    else:
        lines.append("CONTROL FIRED (no-ls-files): %d _git call sites read out of "
                     "the AST, subcommands %s -- none reads the INDEX and none is "
                     "outside the allowlist. Enumeration is diff-tree between two "
                     "TREES." % (len(subcmds), sorted(subcmds)))

    # --- 0c: the read-only allowlist refuses a write ----------------------
    wrote = False
    try:
        _git(["add", "-A"], root)
        wrote = True
    except Refusal as exc:
        lines.append("CONTROL FIRED (git allowlist): %s" % str(exc).split(".")[0])
    if wrote:
        problems.append("CONTROL FAILED (git allowlist): `git add -A` was not refused.")

    # --- 0d: the CLI never constructs a mutation --------------------------
    if CLEAN != Mutations(False, False, False, False, False, False, False, False):
        problems.append("CONTROL FAILED (mutations): CLEAN is not all-False.")
    elif src.count("mut=CLEAN") < 1 or "Mutations(" not in src:
        problems.append("CONTROL FAILED (mutations): mutation plumbing not as claimed.")
    else:
        lines.append("CONTROL FIRED (mutations): the shipped default is all-False; "
                     "every mutant is constructed inside --selftest only.")

    # --- synthetic control trees, per the spec's table --------------------
    def files(k, size, prefix="cases/X/f", status="A"):
        return [Change("%s%03d.txt" % (prefix, i), status, size, 0) for i in range(k)]

    MAN = "COMMIT_MANIFEST.md"
    man_text = "Landing the F99 grid family.\n- 51 case files: the ladder\ntotal: 51 files\n"

    c1 = files(50, 98_000)                                  # 50 files, 4.9 MB
    c2 = files(51, 10)                                      # 51 files
    c3 = [Change("cases/X/big.dat", "A", BYTES_MAX + 1, 0)]  # 5 MB + 1 byte
    c4 = files(51, 10) + [Change(MAN, "A", len(man_text), 0)]
    # AMENDMENT 3 CHANGES THESE TWO CONTROLS' TREES, DECLARED NOT SLID IN. The
    # frozen spec's control table wrote control 5 as
    # `verification/runs/X/log.solve` -> refuse LOGS and control 6 as the same
    # path WITH a manifest -> refuse LOGS anyway. That exact tree is now the
    # ACCEPTING control L3a: the amendment IS the flip. Controls 5 and 6 keep
    # their PURPOSE -- LOGS fires, and a manifest does not exempt it -- by moving
    # to a path outside a run tree, where the clause still has all its teeth.
    # The expectation was not edited to fit; the tree was moved and the old tree
    # is retained below with its new, opposite expectation asserted.
    c5 = [Change("cases/X/log.solve", "A", 100, 0)]
    c6 = list(c5) + [Change(MAN, "A", len(man_text), 0)]
    # AMENDMENT 3 controls. L3a is the pre-amendment control-5 tree, verbatim.
    c5r = [Change("verification/runs/X/log.solve", "A", 100, 0)]
    c5o = [Change("cases/F27_WOMERSLEY_PIPE/log.solve", "A", 100, 0)]
    c5b = [Change("verification/runs/X/log.solve", "A", 40_000_000, 0)]
    c5n = [Change("verification/runs/X/S%03d/log.solve" % i, "A", 100, 0)
           for i in range(51)]
    c7 = [Change("cases/X/attempt3/case.foam", "A", 100, 0)]
    # AMENDMENT 1 (c): a HIDDEN attempt directory is still an attempt directory.
    c7d = [Change("cases/X/.attempt1_stale/S_KE_x/0/T", "A", 100, 0)]
    # AMENDMENT 1 (d): a FILED run output under verification/runs/ is not one.
    c7r = [Change("verification/runs/F6a_GREENBLATT_runs/attempt3_Re936k/"
                  "grading.json", "A", 100, 0)]
    mtx = {MAN: man_text}

    table = [
        ("control 1  50 files / 4.9 MB / no manifest", c1, {}, set(), True),
        ("control 2  51 files / no manifest", c2, {}, {"COUNT"}, False),
        ("control 3  5 MB + 1 byte / no manifest", c3, {}, {"BYTES"}, False),
        ("control 4  51 files WITH manifest", c4, mtx, set(), True),
        ("control 5  one log.solve", c5, {}, {"LOGS"}, False),
        ("control 6  one log.solve WITH manifest", c6, mtx, {"LOGS"}, False),
        ("control 7  one attempt3/ path", c7, {}, {"ATTEMPT"}, False),
        ("control 7d AMENDMENT 1(c)  hidden .attempt1_stale/ outside a run tree",
         c7d, {}, {"ATTEMPT"}, False),
        ("control 7r AMENDMENT 1(d)  attempt3_Re936k/ UNDER verification/runs/",
         c7r, {}, set(), True),
        ("control L3a AMENDMENT 3  verification/runs/X/log.solve ALONE "
         "(this is the pre-amendment control-5 tree; it REFUSED LOGS before)",
         c5r, {}, set(), True),
        ("control L3b AMENDMENT 3  the SAME basename outside a run tree, "
         "cases/F27_WOMERSLEY_PIPE/log.solve", c5o, {}, {"LOGS"}, False),
        ("control L3c AMENDMENT 3  40 MB verification/runs/X/log.solve, NO "
         "manifest -- the exemption must not open a bulk hole",
         c5b, {}, {"BYTES"}, False),
        ("control L3d AMENDMENT 3  51 exempt run-tree log.solve paths, NO "
         "manifest -- COUNT is untouched and still catches bulk",
         c5n, {}, {"COUNT"}, False),
    ]
    for name, ch, mt, want, accept in table:
        f, _ = evaluate(ch, mt)
        got = {x.split(":", 1)[0] for x in f}
        if accept and f:
            problems.append("%s FAILED: expected ACCEPT, refused by %s" % (name, sorted(got)))
        elif not accept and got != want:
            problems.append("%s FAILED: expected exactly %s, got %s"
                            % (name, sorted(want), sorted(got) or "NO REFUSAL"))
        else:
            lines.append("%s: %s" % (name, "ACCEPTED, rc 0" if accept
                                     else "refused %s, rc 2" % sorted(got)))

    # --- control: an empty enumeration REFUSES, it does not accept --------
    f, _ = evaluate([], {})
    if {x.split(":", 1)[0] for x in f} != {"EMPTY"}:
        problems.append("EMPTY CONTROL FAILED: a guard handed zero paths returned "
                        "%s; it must refuse, never report 'small enough'." % (f or "ACCEPT"))
    else:
        lines.append("EMPTY CONTROL FIRED: zero changed paths REFUSES under EMPTY, "
                     "so an enumeration that saw nothing cannot pass vacuously.")

    # --- control 8: 05241ab2's REAL tree, replayed through the adapter ----
    named = "05241ab2"
    if _git(["cat-file", "-e", named + "^{commit}"], root).returncode != 0:
        problems.append("CONTROL 8 FAILED: %s is not a commit here." % named)
    else:
        real = changes_from_trees(named + "^", named, root)
        mts = manifest_texts_from_tree(real, named, root)
        f, notes = evaluate(real, mts)
        got = {x.split(":", 1)[0] for x in f}
        # AMENDMENT 3 CHANGES THIS EXPECTATION, DECLARED NOT SLID IN. Before:
        # {COUNT, LOGS} <= got. All 28 of this commit's log paths sit under
        # verification/runs/ (measured), so LOGS no longer fires on it -- which
        # is the amendment's own evidentiary basis: 05241ab2 was a TRUE positive
        # on BYTES (276.7 MB), a FALSE one on LOGS. The control is STRENGTHENED,
        # not weakened: BYTES is now asserted where it was previously unasserted,
        # and the archetype must still refuse.
        if not {"COUNT", "BYTES"} <= got:
            problems.append("CONTROL 8 FAILED: %s must refuse COUNT + BYTES; got %s. "
                            "It is the measurement that sized the thresholds, and "
                            "AMENDMENT 3 rests on it being a BYTES catch."
                            % (named, sorted(got)))
        elif "LOGS" in got:
            problems.append("CONTROL 8 FAILED: %s still refuses LOGS, but all 28 of "
                            "its log paths are under verification/runs/ and "
                            "AMENDMENT 3 exempts them. The exemption is not reaching "
                            "the real git adapter." % named)
        else:
            live = [c for c in real if c.status in ("A", "M")]
            lines.append("CONTROL 8 FIRED (%s replayed through the real git "
                         "adapter): %d paths added/modified, refused %s. That "
                         "commit is the MEASUREMENT that sized these thresholds, "
                         "not a rebuke of the team that landed it."
                         % (named, len(live), sorted(got)))

    # --- planted failures: each must FLIP its control ---------------------
    plants = [
        ("disable COUNT", c2, {}, Mutations(disable_count=True), "control 2"),
        ("disable BYTES", c3, {}, Mutations(disable_bytes=True), "control 3"),
        ("disable LOGS", c5, {}, Mutations(disable_logs=True), "control 5"),
        ("disable LOGS", c6, mtx, Mutations(disable_logs=True), "control 6"),
        ("disable ATTEMPT", c7, {}, Mutations(disable_attempt=True), "control 7"),
        ("WIDEN the manifest exemption to LOGS", c6, mtx,
         Mutations(manifest_exempts_logs=True), "control 6"),
        ("disable ATTEMPT", c7d, {}, Mutations(disable_attempt=True), "control 7d"),
    ]
    for what, ch, mt, mut, which in plants:
        f, _ = evaluate(ch, mt, mut)
        if f:
            problems.append("PLANT DID NOT FLIP (%s): %s was still refused by %s. "
                            "The clause credited with that refusal is not the one "
                            "producing it." % (what, which, [x.split(':')[0] for x in f]))
        else:
            tail = ("  <-- this is the defect the spec FORBIDS, shown "
                    "reintroducible AND shown caught" if mut.manifest_exempts_logs else "")
            lines.append("PLANT FLIPPED %s (%s): the tree became ACCEPTED, so the "
                         "clause is load-bearing and reachable.%s" % (which, what, tail))
    # AMENDMENT 1 (d) is an EXEMPTION, so its planted failure runs the other
    # way: removing it must make an ACCEPTING control REFUSE. An exemption that
    # cannot be shown to change an outcome is not known to be doing anything.
    fr, _ = evaluate(c7r, {}, Mutations(disable_runs_exemption=True))
    if "ATTEMPT" not in {x.split(":", 1)[0] for x in fr}:
        problems.append("PLANT DID NOT FLIP (remove the verification/runs/ "
                        "exemption): control 7r stayed ACCEPTED, so the exemption "
                        "is not what is accepting it.")
    else:
        lines.append("PLANT FLIPPED control 7r (remove the verification/runs/ "
                     "exemption): the filed run output became REFUSED under "
                     "ATTEMPT, so AMENDMENT 1(d) is load-bearing and is the only "
                     "thing standing between this guard and refusing every "
                     "legitimate re-attempt the lab files.")

    # AMENDMENT 3 is an EXEMPTION, so its planted failure runs the OTHER way,
    # exactly as AMENDMENT 1 (d)'s does: removing it must make an ACCEPTING
    # control REFUSE. An exemption that cannot be shown to change an outcome is
    # not known to be doing anything.
    fl, _ = evaluate(c5r, {}, Mutations(disable_logs_runs_exemption=True))
    if "LOGS" not in {x.split(":", 1)[0] for x in fl}:
        problems.append("PLANT DID NOT FLIP (remove the verification/runs/ LOGS "
                        "exemption): control L3a stayed ACCEPTED, so the exemption "
                        "is not what is accepting it and AMENDMENT 3 is unproven.")
    else:
        lines.append("PLANT FLIPPED control L3a (remove the verification/runs/ LOGS "
                     "exemption): the filed solver log became REFUSED under LOGS, "
                     "so AMENDMENT 3 is load-bearing -- and it is the only thing "
                     "standing between this guard and a clause measured at 0 true "
                     "/ 14 false on 200 real commits.")

    # ...and the SHIPPED code must not be any of the mutants.
    f6, _ = evaluate(c6, mtx)
    if "LOGS" not in {x.split(":", 1)[0] for x in f6}:
        problems.append("PLANT RESIDUE: the SHIPPED guard let a manifest exempt a "
                        "log. The mutant escaped the selftest.")
    else:
        lines.append("PLANT RESIDUE CHECK: the shipped guard still refuses control "
                     "6 under LOGS, so no mutant leaked into shipped behaviour.")

    # --- AMENDMENT 2: the EMPTY merge carve-out, and its L-314 proof ------
    # E1 uses the REAL commit 5e45a5a9 -- characterised BY COMMAND, not by the
    # shape expected of it: it has ONE parent and its tree equals that parent's.
    # A lane read `git rev-list --parents -n1 | wc -w` = 2 as "two parents" when
    # it is sha + one parent, and reported a merge that does not exist. The
    # control uses the measurement, never the expectation.
    e1_sha = "5e45a5a9"
    if _git(["cat-file", "-e", e1_sha + "^{commit}"], root).returncode != 0:
        problems.append("E1 CONTROL FAILED: %s is not a commit here." % e1_sha)
    else:
        e1_meta = commit_meta_from_sha(e1_sha, root)
        e1_ch = changes_from_trees(e1_sha + "^", e1_sha, root)
        if e1_meta is None or e1_meta.n_parents != 1 or not e1_meta.tree_equals_first_parent:
            problems.append("E1 CONTROL FAILED: %s is not the single-parent "
                            "zero-path shape this control needs; read %s."
                            % (e1_sha, e1_meta))
        elif e1_ch:
            problems.append("E1 CONTROL FAILED: %s enumerated %d paths, expected 0."
                            % (e1_sha, len(e1_ch)))
        else:
            f, _ = evaluate(e1_ch, {}, CLEAN, e1_meta)
            if {x.split(":", 1)[0] for x in f} != {"EMPTY"}:
                problems.append("E1 CONTROL FAILED: a REAL single-parent empty "
                                "commit must still refuse EMPTY; got %s." % (f or "ACCEPT"))
            else:
                lines.append("E1 CONTROL FIRED (%s, real, 1 parent, tree == parent "
                             "tree, 0 paths): still REFUSES under EMPTY, so the "
                             "merge carve-out does not reach a non-merge." % e1_sha)
            f2, n2 = evaluate([], {}, CLEAN, CommitMeta(2, True))
            if f2:
                problems.append("E2 CONTROL FAILED: a 2-parent commit whose tree "
                                "equals its first parent's must be carved out; got %s." % f2)
            elif not any(n.startswith("MERGE:") for n in n2):
                problems.append("E2 CONTROL FAILED: the carve-out was SILENT. It must "
                                "emit a MERGE note -- a carve-out that hides is a hole.")
            else:
                lines.append("E2 CONTROL FIRED (2 parents, tree == first parent's): "
                             "EMPTY carved out AND reported as a distinct MERGE note.")
            f3, _ = evaluate(e1_ch, {}, Mutations(widen_merge_carveout=True), e1_meta)
            if f3:
                problems.append("PLANT DID NOT FLIP (widen the merge carve-out to "
                                "single-parent): E1 stayed refused by %s. The carve-out "
                                "would then be an UNTESTED HOLE in the one clause "
                                "verification ruled load-bearing." % f3)
            else:
                lines.append("PLANT FLIPPED E1 (widen the merge carve-out to "
                             "single-parent commits): the REAL empty commit became "
                             "ACCEPTED -- the parent-count condition is exactly what "
                             "keeps EMPTY alive, and widening it is detectable.")

    # --- control 9: L-314, a caller that ignores `set -e` still detects ---
    with tempfile.TemporaryDirectory() as td:
        me = Path(__file__).resolve()
        hz = subprocess.run(["bash", "-c",
                             "python3 %s --commit %s > %s/hz.txt 2>&1\necho SWALLOWED\n"
                             % (me, named, td)], capture_output=True, text=True)
        if hz.returncode != 0 or "SWALLOWED" not in hz.stdout:
            problems.append("L-314 HAZARD CONTROL FAILED: expected the ignoring "
                            "caller to run on and exit 0; got rc %d." % hz.returncode)
        else:
            lines.append("L-314 HAZARD SHOWN LIVE: a caller that does not test rc ran "
                         "the refusing guard, continued past it and exited 0. `set -e` "
                         "is not in force here; a printed refusal would have been lost.")
        ck = subprocess.run(["bash", "-c",
                             "rc=0\npython3 %s --commit %s > %s/ck.txt 2>&1 || rc=$?\n"
                             "echo RC=$rc\necho REACHED_ANYWAY\n" % (me, named, td)],
                            capture_output=True, text=True)
        txt = (Path(td) / "ck.txt").read_text() if (Path(td) / "ck.txt").exists() else ""
        rcl = [l for l in ck.stdout.splitlines() if l.startswith("RC=")]
        if not rcl or rcl[0] != "RC=2":
            problems.append("L-314 CONTROL FAILED: refusing run did not return rc 2 "
                            "to a caller that tested it; saw %s" % (rcl or "no RC line"))
        elif "REACHED_ANYWAY" not in ck.stdout:
            problems.append("L-314 CONTROL FAILED: caller never reached the line "
                            "after the rc test.")
        elif "REFUSED" not in txt or not any(
                ("    %s:" % c) in txt for c in ("COUNT", "BYTES", "LOGS", "ATTEMPT", "EMPTY")):
            problems.append("L-314 CONTROL FAILED: rc 2 returned but the output "
                            "carries no greppable REFUSED line and named clause.")
        else:
            lines.append("L-314 CONTROL FIRED: with NO `set -e`, a caller that tested "
                         "rc read RC=2, reached the line after it, and the output "
                         "carries a greppable REFUSED line and a named clause -- the refusal "
                         "survives the exact shell shape that swallowed it above.")

    for l in lines:
        print("  " + l)
    if problems:
        print("")
        for p in problems:
            print("  " + p)
        print("\nSELFTEST FAILED: %d control(s) did not behave." % len(problems))
        return 2
    print("\nSELFTEST PASS: %d controls fired, each shown able to fail." % len(lines))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=(
        "Report on a tree's size and content. Never acts: no kill, no delete, "
        "no git write, no index, and it never writes your manifest."))
    ap.add_argument("--base", default="HEAD", help="base tree-ish (default HEAD)")
    ap.add_argument("--tree", help="candidate tree-ish (e.g. a write-tree result)")
    ap.add_argument("--commit", help="replay a commit against its first parent")
    ap.add_argument("--json", action="store_true", help="machine-readable verdict")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    ast_n = count_assert_nodes(Path(__file__).read_text())
    if ast_n:
        print("REFUSED (instrument): %d assert(s) present; -O would delete them "
              "(L-332)." % ast_n)
        return 2

    root = repo_root(Path(__file__).resolve().parent)
    if a.commit:
        base, tree, label = a.commit + "^", a.commit, "commit " + a.commit
    elif a.tree:
        base, tree, label = a.base, a.tree, "tree %s vs %s" % (a.tree, a.base)
    else:
        print("usage: give --tree <tree-ish> (with optional --base) or --commit <sha>")
        return 1

    changes = changes_from_trees(base, tree, root)
    meta = commit_meta_from_sha(a.commit, root) if a.commit else None
    findings, notes = evaluate(changes, manifest_texts_from_tree(changes, tree, root),
                               CLEAN, meta)
    if a.json:
        print(json.dumps({"label": label,
                          "verdict": "REFUSED" if findings else "ACCEPTED",
                          "clauses": sorted({f.split(":", 1)[0] for f in findings}),
                          "findings": findings, "notes": notes}, indent=1))
        return 2 if findings else 0
    return report(findings, notes, label)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        sys.exit(2)
