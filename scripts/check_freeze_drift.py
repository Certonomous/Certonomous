#!/usr/bin/env python3
"""FREEZE-DRIFT SWEEP -- is the frozen file the file on disk?

WHAT THIS MEASURES, AND WHY NOTHING ELSE IN THE LAB DOES IT
-----------------------------------------------------------
Standing rule 2 ends with an instruction nothing in this repository carried
out corpus-wide: "verify the frozen file IS the file that ran by hashing it
against the committed blob."  A pre-registration's entire evidentiary content
is the freeze.  If the bytes a reader opens off disk are not the bytes
committed at HEAD, the freeze proves nothing about what that reader just read,
and the failure is SILENT -- both files exist, both parse, both look frozen.

Two real instances, both found 2026-09-12, are the two directions of one
disease -- THE ARTIFACT AND THE BYTES THAT MADE IT ARE NOT BOTH AT HEAD:

  (i)  verification/campaign/CRM_WINGALONE_FLOW_PREREGISTRATION.md is tracked
       at HEAD as one blob while the file ON DISK hashes to a different one --
       the content of an earlier, deliberately UNSIGNED draft.  The signed
       freeze exists only as a git blob, staged from somewhere that was never
       the working tree.  Any agent opening that path off disk reads an
       unsigned pre-registration and cannot tell.
  (ii) The converse: a graded birth certificate tracked in the repo carrying
       schema fields that exist ONLY in an uncommitted file -- an artifact
       unreproducible from HEAD.

This sweep measures direction (i) over the whole corpus of frozen documents,
and names direction (ii)'s shape as UNTRACKED-ON-DISK.

THE ONLY INDEX-IMMUNE COMPARISON, AND WHY NOTHING ELSE IS USED
---------------------------------------------------------------
`git status`, `git diff`, `git diff HEAD`, `git ls-files` and `git show
:<path>` ALL CONSULT THE SHARED INDEX.  On this box the shared index stages
hundreds of differences of which the great majority are BYTE-IDENTICAL to HEAD
on disk (verification, 2026-08-30: 431 staged differences, 372 byte-identical
to HEAD).  Every one of those instruments therefore MISREPORTS here, and
misreports STABLY -- rerunning them does not help.  This file uses exactly two
git reads per path and no others:

    git rev-parse <HEAD-sha>:<repo-relative-path>  -> the blob at HEAD, or rc!=0
    git hash-object <path>                         -> the blob of the disk bytes

plus one TREE read, `git ls-tree -r --name-only <HEAD-sha>`, to enumerate the
population.  A tree read is not an index read.  `_git()` enforces the
allowlist BY RAISING, so the restriction is a refusal in code and not a
convention in a comment.  Pattern and discipline follow the prior art in
verification/credibility/vr6_untracked_launch_record.py.

HEAD IS PINNED ONCE.  Peers commit constantly on this box; resolving HEAD per
path would let the baseline move mid-sweep and produce a table no single
commit ever explains.  The sha is captured once and printed beside the counts.

THE FOUR STATES, KEPT DISTINCT
-------------------------------
    IDENTICAL         blob at HEAD == bytes on disk.  The freeze holds.
    DRIFTED           both exist, hashes differ.  The CRM class.  A reader
                      opening this path does NOT read what was frozen.
    ABSENT-FROM-DISK  tracked at HEAD, no file on disk.
    UNTRACKED-ON-DISK a matching file on disk with no blob at HEAD -- a frozen
                      document that exists nowhere but this working tree.

A FIFTH STATE THE FIRST FOUR ARE STRUCTURALLY BLIND TO
-------------------------------------------------------
    DUPLICATE-BASENAME  one basename at two or more distinct TRACKED paths.
                        DIVERGENT when the blobs differ; MIRRORED when they
                        are byte-identical.

The first four states ask, of each path independently, "does the disk agree
with HEAD".  TWO TRACKED COPIES OF ONE PRE-REGISTRATION THAT DISAGREE WITH
EACH OTHER PASS THAT QUESTION TWICE: each file hashes equal to its OWN blob,
so BOTH read IDENTICAL and the sweep returns clean while two divergent freezes
for one campaign sit at HEAD and one of them is stale.  Live instance, found
2026-09-12: `PRD_E1_PREREGISTRATION.md` exists at both
`verification/campaign/` and `docs/campaigns/navier_class/PRD/`, and the
second pins a SUPERSEDED comparator sha with no addendum.  A sweep that
returns a green over exactly the condition it exists to detect is the defect
class this team audits, so DIVERGENT GATES and the four-state model does not
ship alone.

MIRRORED is reported and NOT gated: a byte-identical copy is redundancy, not a
contradiction.  Only disagreement is a finding.

DRIFTED is NOT a defect verdict and this instrument REPAIRS NOTHING.  An
uncommitted difference is somebody's unfinished work and is inspected, never
reverted (standing rule 10); the file belongs to the team that froze it.  The
output is a measurement and a roll call.

THE CONTROL (standing rule 3)
------------------------------
A zero from a reader not shown able to see a non-zero is not evidence.  All
four states are therefore planted and read back THROUGH THE REAL CLASSIFIER
before any live count is believed.  The plants are built in a THROWAWAY GIT
REPOSITORY under the scratchpad: NO REAL PRE-REGISTRATION IS EVER MODIFIED,
MOVED OR DELETED TO PLANT ANYTHING.  The fixture builder refuses to run
anywhere that could be the real repository.

EXIT CODES
----------
    0   no DRIFTED, no ABSENT-FROM-DISK and no DIVERGENT duplicate basename
    3   at least one DRIFTED, ABSENT-FROM-DISK or DIVERGENT
    2   a control limb misbehaved -- REFUSE, never degrade

WHAT THIS CHECK CANNOT SEE
---------------------------
Recorded here, in the instrument, because the limitations section is where a
reader goes to learn what the green does not cover.  A green over a property
nobody asserts is SILENCE about it, not evidence.

 1. WHETHER A DRIFT IS BENIGN OR SERIOUS.  A hash mismatch is direction-free.
    The first live sweep found both directions in one run: one path was HEAD
    plus 232 appended lines (a correctly-formed pre-first-compute amendment,
    simply not committed yet) and another was HEAD MINUS its signature block
    (a working tree that never held the signed freeze at all).  Both read
    DRIFTED and only READING BOTH BLOBS separates them.  Direction-of-diff is
    a necessary discriminator and NOT a sufficient one.

 2. A GIT FAILURE IS READ AS "NOT TRACKED".  `_git(..., check=False)` returns
    None on ANY non-zero rc, and `classify` reads a None from `rev-parse
    <HEAD>:<path>` as "no blob at HEAD" -> UNTRACKED-ON-DISK.  A genuine git
    error takes the same path and would inflate UNTRACKED rather than refuse.
    The pinned HEAD is resolved with check=True first, which makes the bad-sha
    case unreachable, so this is narrow -- but it is the `broken` vs
    `unverified` conflation this lab collects, and it is DISCLOSED rather than
    silently relied upon.

 3. WHETHER THE FROZEN DOCUMENT WAS EVER EXECUTED.  Identical bytes prove the
    reader reads what was frozen; they say nothing about whether the frozen
    grader ran, or whether its controls fired.  That is the L-544
    execution-witness gap and it is not addressed here.

 4. [CLOSED 2026-09-12 -- kept because the blind spot is worth remembering.]
    TWO TRACKED COPIES OF ONE FROZEN DOCUMENT THAT DISAGREE were invisible to
    the original four states: each copy hashes equal to its OWN blob, so both
    read IDENTICAL and the sweep reported clean while two divergent freezes for
    one campaign sat at HEAD.  A live instance exists (`PRD_E1_PREREGISTRATION
    .md` at two paths, one pinning a superseded comparator blob).  The
    DUPLICATE-BASENAME limb (DIVERGENT / MIRRORED, limbs P5a-P5c) now covers
    it.  THE LESSON THAT OUTLIVES THE FIX: a per-path identity check is
    structurally unable to see a disagreement BETWEEN paths, and it reports
    that blindness as a green.

 5. THE DISK WALK IS UNPRUNED.  `disk_population` descends every directory but
    `.git`, including `processor*/`, `VTK/`, `postProcessing/` and every
    numeric time directory -- the same IO shape this team charged against
    `check_comparator_freeze.py`, where 87.4 % of the walk was solver output.
    Measured at 7.69 s wall today and therefore affordable; it grows with the
    run corpus, and it is named now rather than rediscovered later.
"""
import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# The population: frozen documents.  Matched on the BASENAME.
PATTERNS = ("*PREREGISTRATION*.md", "*_AMENDMENT.md")

# Read-only, INDEX-FREE git.  `status`, `diff`, `ls-files`, `add`, `show` and
# every other subcommand are REFUSED here rather than merely avoided by habit.
# `ls-tree` reads a TREE, not the index.  `show` is absent because this sweep
# never needs tracked CONTENT -- only tracked HASHES -- and `git show :<path>`
# is one keystroke from the index.
GIT_ALLOW = {"rev-parse", "hash-object", "ls-tree"}

IDENTICAL = "IDENTICAL"
DRIFTED = "DRIFTED"
ABSENT = "ABSENT-FROM-DISK"
UNTRACKED = "UNTRACKED-ON-DISK"
STATES = (IDENTICAL, DRIFTED, ABSENT, UNTRACKED)

# The fifth state is a property of a GROUP of paths, not of one path, which is
# exactly why the per-path states cannot express it.
DIVERGENT = "DIVERGENT"
MIRRORED = "MIRRORED"


def _git(args, cwd, check=False):
    """The single door to git.  Raises on any subcommand outside the allowlist."""
    if args[0] not in GIT_ALLOW:
        raise RuntimeError(
            "check_freeze_drift refuses git subcommand %r: only %s are "
            "index-free reads. status/diff/ls-files/show consult the SHARED "
            "INDEX, which misreports on this box and does so stably."
            % (args[0], sorted(GIT_ALLOW)))
    p = subprocess.run(["git"] + args, cwd=str(cwd),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        if check:
            raise RuntimeError("git %s failed in %s: %s"
                               % (args[0], cwd, p.stderr.decode().strip()))
        return None
    return p.stdout.decode().strip()


def matches(name):
    return any(fnmatch.fnmatch(name, pat) for pat in PATTERNS)


# --------------------------------------------------------------------------
# THE READER -- the single door.  The live sweep and every control limb enter
# here.  The question asked of each path is `do the blob at HEAD and the bytes
# on disk agree`, never `do these bytes exist somewhere in history`.
# --------------------------------------------------------------------------
def classify(repo, rel, head_sha):
    """Return (state, head_blob_or_None, disk_blob_or_None) for one repo-relative path."""
    head = _git(["rev-parse", "%s:%s" % (head_sha, rel)], cwd=repo)
    disk_path = Path(repo) / rel
    disk = (_git(["hash-object", str(disk_path)], cwd=repo)
            if disk_path.is_file() else None)
    if head is not None and disk is not None:
        return (IDENTICAL if head == disk else DRIFTED), head, disk
    if head is not None and disk is None:
        return ABSENT, head, None
    if head is None and disk is not None:
        return UNTRACKED, None, disk
    return None, None, None          # neither: not a member of any population


def tracked_population(repo, head_sha):
    """Every path tracked at HEAD whose basename matches.  A TREE read, not an index read."""
    out = _git(["ls-tree", "-r", "--name-only", head_sha], cwd=repo, check=True)
    return sorted(p for p in out.splitlines()
                  if p and matches(os.path.basename(p)))


def disk_population(repo):
    """Every matching file ON DISK, repo-relative.  Needed for UNTRACKED-ON-DISK,
    which a tree read cannot see by construction."""
    out = []
    repo = Path(repo)
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if matches(f):
                out.append(Path(root, f).relative_to(repo).as_posix())
    return sorted(out)


#: Boilerplate a frozen document's basename is built from.  A name left EMPTY
#: after these are stripped carries NO campaign identity -- `PREREGISTRATION.md`
#: is the lab's ordinary per-case filename and the CASE DIRECTORY is what
#: identifies it.  Grouping those by basename asks "do 222 different campaigns
#: disagree with each other", which is not a question, and gating on the answer
#: fires the alarm on the normal case.  A gate that fires on the normal case is
#: retired by its readers within a day, and a guard nobody trusts costs this lab
#: more than a flag nobody remembers.
_NAME_BOILERPLATE = re.compile(
    r"(PREREGISTRATION|AMENDMENT|DRAFT|SUCCESSOR|\.md)", re.I)


def campaign_identity(basename):
    """The campaign id carried by a basename, or None when the name carries none.

    `PRD_E1_PREREGISTRATION.md` -> `PRD_E1`   (the name identifies the campaign)
    `PREREGISTRATION.md`        -> None       (the DIRECTORY identifies it)
    """
    stem = _NAME_BOILERPLATE.sub("", basename)
    stem = re.sub(r"[^A-Za-z0-9]+", "", stem)
    return stem or None


def duplicate_basenames(rows):
    """Group the TRACKED population by basename; return the groups of size >= 2.

    ONLY basenames carrying a campaign identity are grouped -- see
    `campaign_identity`. Generic names are counted and DISCLOSED in the output,
    never silently dropped: a prune that quietly removes rows from a judged
    population is a FAIL-OPEN, which is the class this team collects.

    Keyed on the blob AT HEAD, never on the disk bytes: the question is whether
    the REPOSITORY holds two freezes for one document, which is true or false
    independently of anybody's working tree. A row with no blob at HEAD
    (UNTRACKED-ON-DISK) is not part of the tracked population and cannot make a
    duplicate here.

    DIVERGENT when the group holds two or more distinct blobs -- two freezes
    for one campaign that DISAGREE, at least one of them stale.
    MIRRORED when every path in the group carries the same blob -- redundancy,
    not a contradiction, and so reported rather than gated."""
    groups, generic = {}, {}
    for r in rows:
        if r["head"] is None:
            continue
        base = os.path.basename(r["path"])
        (groups if campaign_identity(base) else generic).setdefault(
            base, []).append(r)
    out = []
    for base, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        blobs = {m["head"] for m in members}
        out.append(dict(basename=base,
                        kind=(MIRRORED if len(blobs) == 1 else DIVERGENT),
                        n_blobs=len(blobs),
                        members=sorted(members, key=lambda m: m["path"])))
    skipped = {b: len(m) for b, m in generic.items() if len(m) >= 2}
    return out, skipped


def sweep(repo, head_sha):
    """The whole corpus: union of tracked-at-HEAD and on-disk, one classify per path."""
    paths = sorted(set(tracked_population(repo, head_sha)) | set(disk_population(repo)))
    rows = []
    for rel in paths:
        state, head, disk = classify(repo, rel, head_sha)
        if state is not None:
            rows.append(dict(path=rel, state=state, head=head, disk=disk))
    return rows


# --------------------------------------------------------------------------
# CONTROLS -- four limbs, one per state, in a THROWAWAY repository.
# --------------------------------------------------------------------------
def _fixture_git(args, cwd):
    """Write-capable git for the SCRATCH FIXTURE ONLY.

    Deliberately NOT `_git`: the allowlist there must stay a refusal that no
    fixture need ever widen.  This function instead refuses to run anywhere
    that could be the real repository -- the plants can only ever touch a
    throwaway tree, so NO REAL PRE-REGISTRATION IS EVER MODIFIED TO PLANT
    ANYTHING."""
    cwd = Path(cwd).resolve()
    if cwd == REPO or REPO in cwd.parents or cwd in REPO.parents:
        raise RuntimeError("fixture git refuses to run at or around the real "
                           "repository: %s" % cwd)
    if ".freeze_drift_control_" not in str(cwd):
        raise RuntimeError("fixture git refuses a cwd that is not a control "
                           "fixture: %s" % cwd)
    p = subprocess.run(["git"] + args, cwd=str(cwd),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("fixture git %s failed: %s"
                           % (args[0], p.stderr.decode().strip()))
    return p.stdout.decode().strip()


def controls(verbose=True):
    """Plant all four states and require the REAL classifier to read each one back.

    Returns (ok, results) where results maps limb -> (expected, got, passed)."""
    results = {}
    tmp = None
    scratch = os.environ.get("CLAUDE_SCRATCH") or tempfile.gettempdir()
    try:
        tmp = Path(tempfile.mkdtemp(dir=scratch, prefix=".freeze_drift_control_"))
        _fixture_git(["init", "-q", "-b", "main", "."], cwd=tmp)
        _fixture_git(["config", "user.email", "control@localhost"], cwd=tmp)
        _fixture_git(["config", "user.name", "freeze-drift control"], cwd=tmp)

        # Three tracked members of the population, committed so they exist at HEAD.
        committed = {
            "P1_PREREGISTRATION.md": "# P1 identical\nfrozen line\n",
            "P2_PREREGISTRATION.md": "# P2 will drift\nfrozen line\n",
            "P3_T1b_L4_AMENDMENT.md": "# P3 will vanish from disk\nfrozen line\n",
            # P5d: the GENERIC basename, the lab's ordinary per-case filename,
            # at two paths with DIFFERENT bytes. It must NOT be grouped and
            # must NOT gate -- these are two different campaigns, identified by
            # their directories, and flagging them fires on the normal case.
            "gen1/PREREGISTRATION.md": "# campaign one\nfrozen\n",
            "gen2/PREREGISTRATION.md": "# campaign TWO, different bytes\nfrozen\n",
            # A non-member, to prove the population filter excludes it.
            "README.md": "not a frozen document\n",
            # P5a: ONE basename at TWO tracked paths with DIFFERENT bytes --
            # the PRD_E1 class. Both hash equal to their OWN blob, so both read
            # IDENTICAL and only the group check can see the contradiction.
            "a/P5A_PREREGISTRATION.md": "# P5A\ncomparator pin 1111111111\n",
            "b/P5A_PREREGISTRATION.md": "# P5A\ncomparator pin 2222222222 SUPERSEDED\n",
            # P5b: one basename at two tracked paths, BYTE-IDENTICAL.
            "a/P5B_PREREGISTRATION.md": "# P5B\nidentical in both places\n",
            "b/P5B_PREREGISTRATION.md": "# P5B\nidentical in both places\n",
            # P5c: a basename unique in the tree -- must be in NEITHER group.
            "a/P5C_PREREGISTRATION.md": "# P5C\nunique basename\n",
        }
        for name, text in committed.items():
            (tmp / name).parent.mkdir(parents=True, exist_ok=True)
            (tmp / name).write_text(text)
        _fixture_git(["add", "--"] + sorted(committed), cwd=tmp)
        _fixture_git(["commit", "-q", "-m", "control fixture"], cwd=tmp)
        head_sha = _fixture_git(["rev-parse", "HEAD"], cwd=tmp)

        # Now perturb the working tree into the other three states.
        (tmp / "P2_PREREGISTRATION.md").write_text(
            "# P2 will drift\nfrozen line\nA BYTE THAT WAS NEVER COMMITTED\n")
        (tmp / "P3_T1b_L4_AMENDMENT.md").unlink()
        (tmp / "P4_PREREGISTRATION.md").write_text(
            "# P4 exists only in this working tree\n")

        rows = {r["path"]: r for r in sweep(tmp, head_sha)}
        expect = {
            "P1": ("P1_PREREGISTRATION.md", IDENTICAL),
            "P2": ("P2_PREREGISTRATION.md", DRIFTED),
            "P3": ("P3_T1b_L4_AMENDMENT.md", ABSENT),
            "P4": ("P4_PREREGISTRATION.md", UNTRACKED),
        }
        for limb, (rel, want) in expect.items():
            got = rows[rel]["state"] if rel in rows else "(not seen at all)"
            results[limb] = (want, got, got == want)

        # P5a / P5b / P5c -- the GROUP reader, driven on the same sweep output
        # the four per-path limbs above came from.
        _groups, _skipped = duplicate_basenames(list(rows.values()))
        dups = {g["basename"]: g for g in _groups}

        # P5a must ALSO demonstrate the blind spot it exists to close: both of
        # its paths must read IDENTICAL per-path. If they did not, the group
        # check would be catching something the four states already caught, and
        # this limb would prove nothing.
        both_identical = all(rows[p]["state"] == IDENTICAL
                             for p in ("a/P5A_PREREGISTRATION.md",
                                       "b/P5A_PREREGISTRATION.md"))
        got5a = dups["P5A_PREREGISTRATION.md"]["kind"] if "P5A_PREREGISTRATION.md" in dups else "(no group)"
        results["P5a"] = ("DIVERGENT (both paths IDENTICAL per-path)",
                          "%s (both IDENTICAL per-path: %s)" % (got5a, both_identical),
                          got5a == DIVERGENT and both_identical)

        got5b = dups["P5B_PREREGISTRATION.md"]["kind"] if "P5B_PREREGISTRATION.md" in dups else "(no group)"
        results["P5b"] = (MIRRORED, got5b, got5b == MIRRORED)

        # P5d -- THE ASSERTION THAT MAKES THE GENERIC-NAME NARROWING REAL.
        # Without it this suite scores identically with and without the
        # narrowing, and a green over a property nobody asserts is SILENCE.
        results["P5d"] = ("generic basename: not grouped, not gated",
                          "not grouped" if "PREREGISTRATION.md" not in dups
                          else "GROUPED (would gate on the normal case)",
                          "PREREGISTRATION.md" not in dups
                          and _skipped.get("PREREGISTRATION.md") == 2)

        results["P5c"] = ("unique basename: no group",
                          "no group" if "P5C_PREREGISTRATION.md" not in dups
                          else "GROUPED",
                          "P5C_PREREGISTRATION.md" not in dups)

        # A further assertion, not a gated limb: the population filter must have
        # EXCLUDED the non-member, or the four limbs above prove nothing about
        # what the live sweep will enumerate.
        results["POP"] = ("README.md excluded",
                          "excluded" if "README.md" not in rows else "INCLUDED",
                          "README.md" not in rows)

        # And a sixth: the allowlist must actually raise, or "enforced in code"
        # is a claim rather than a fact.
        try:
            _git(["status"], cwd=tmp)
            raised = False
        except RuntimeError:
            raised = True
        results["ALLOWLIST"] = ("git status refused", "refused" if raised
                                else "ALLOWED", raised)

        if verbose:
            for limb in ("P1", "P2", "P3", "P4", "P5a", "P5b", "P5c",
                         "P5d", "POP", "ALLOWLIST"):
                want, got, ok = results[limb]
                print("  control %-9s %s: expected %-22s got %s"
                      % (limb, "PASS" if ok else "FAIL", want, got))
        return all(ok for _, _, ok in results.values()), results
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="drive the seven control limbs only; print PASS/FAIL per limb")
    args = ap.parse_args()

    print("FREEZE-DRIFT SWEEP -- is the frozen file the file on disk? "
          "(standing rule 2)")
    print("  repo=%s" % REPO)
    print("  INSTRUMENTS: `git rev-parse <HEAD>:<path>` vs `git hash-object "
          "<path>`, plus one `git ls-tree -r` for the population. NO status, "
          "NO diff, NO ls-files, NO show -- all consult the SHARED INDEX, "
          "which misreports on this box and does so stably. The allowlist "
          "RAISES.")
    print("  POPULATION PATTERNS: %s (matched on basename)" % (", ".join(PATTERNS)))

    print("CONTROLS (rule 3 -- all FIVE states planted in a THROWAWAY repo and "
          "read back through the REAL classifier; no real pre-registration is "
          "touched):")
    ok, results = controls()
    npass = sum(1 for _, _, o in results.values() if o)
    nstate = sum(1 for k in results if k.startswith("P") and k != "POP")
    print("  control limbs: %d/%d PASS  (%d state limbs P1-P5c, plus POP and "
          "ALLOWLIST as structural assertions)" % (npass, len(results), nstate))
    if not ok:
        print("VERDICT: NOT A RESULT -- a control limb misbehaved. Refusing to "
              "report any live count.")
        return 2
    if args.selftest:
        print("SELFTEST: PASS -- %d/%d limbs" % (npass, len(results)))
        return 0

    head_sha = _git(["rev-parse", "HEAD"], cwd=REPO, check=True)
    print("HEAD PINNED ONCE for the whole sweep: %s" % head_sha)

    rows = sweep(REPO, head_sha)
    counts = {s: sum(1 for r in rows if r["state"] == s) for s in STATES}
    tracked = counts[IDENTICAL] + counts[DRIFTED] + counts[ABSENT]
    print("POPULATION: %d paths in the union (tracked at HEAD: %d, on disk and "
          "matching: %d)"
          % (len(rows), tracked, counts[IDENTICAL] + counts[DRIFTED] + counts[UNTRACKED]))
    print("  %-20s %6d   the freeze holds: disk bytes == committed blob" % (IDENTICAL, counts[IDENTICAL]))
    print("  %-20s %6d   THE FINDING: a reader opening this path does NOT read what was frozen" % (DRIFTED, counts[DRIFTED]))
    print("  %-20s %6d   tracked at HEAD, no file on disk" % (ABSENT, counts[ABSENT]))
    print("  %-20s %6d   frozen document existing nowhere but this working tree" % (UNTRACKED, counts[UNTRACKED]))

    for state in (DRIFTED, ABSENT, UNTRACKED):
        sel = [r for r in rows if r["state"] == state]
        if not sel:
            continue
        print("ROLL CALL -- %s (%d):" % (state, len(sel)))
        for r in sel:
            print("    %-14s HEAD=%s  disk=%s  %s"
                  % (r["state"], (r["head"] or "(none)")[:12],
                     (r["disk"] or "(none)")[:12], r["path"]))

    # The fifth state: a property of a GROUP, invisible to every per-path state
    # above. Both members of a DIVERGENT group are counted IDENTICAL there.
    dups, generic_skipped = duplicate_basenames(rows)
    div = [g for g in dups if g["kind"] == DIVERGENT]
    mir = [g for g in dups if g["kind"] == MIRRORED]
    print("DUPLICATE-BASENAME: %d basename(s) at two or more tracked paths -- "
          "%d DIVERGENT (GATED: two freezes for one document that DISAGREE), "
          "%d MIRRORED (reported, NOT gated: byte-identical copies are "
          "redundancy, not a contradiction)" % (len(dups), len(div), len(mir)))
    # DISCLOSED, never silently pruned: a prune that quietly removes rows from a
    # judged population is a FAIL-OPEN. These names carry no campaign identity,
    # so the CASE DIRECTORY identifies them and a shared basename is the lab's
    # ordinary convention rather than a contradiction.
    if generic_skipped:
        print("  NOT GROUPED (generic basename, identity is the DIRECTORY -- "
              "grouping these would fire on the normal case): %s"
              % ", ".join("%s x%d" % (b, n)
                          for b, n in sorted(generic_skipped.items())))
    for label, sel in ((DIVERGENT, div), (MIRRORED, mir)):
        if not sel:
            continue
        print("ROLL CALL -- DUPLICATE-BASENAME / %s (%d):" % (label, len(sel)))
        for g in sel:
            print("    %s  -- %d paths, %d distinct blob(s)"
                  % (g["basename"], len(g["members"]), g["n_blobs"]))
            for m in g["members"]:
                print("        blob=%s  per-path=%-16s %s"
                      % ((m["head"] or "(none)")[:12], m["state"], m["path"]))

    bad = counts[DRIFTED] + counts[ABSENT] + len(div)
    if bad:
        print("RESULT: %d finding(s) -- DRIFTED, ABSENT-FROM-DISK or DIVERGENT "
              "duplicate basename. This is a "
              "MEASUREMENT AND A ROLL CALL, not a repair order and not a defect "
              "verdict on any team: an uncommitted difference is somebody's "
              "unfinished work and is inspected, NEVER reverted (standing rule "
              "10). Each file belongs to the team that froze it." % bad)
        return 3
    print("RESULT: 0 DRIFTED, 0 ABSENT-FROM-DISK and 0 DIVERGENT across %d "
          "paths -- and the controls above show the reader CAN see all five "
          "states." % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
